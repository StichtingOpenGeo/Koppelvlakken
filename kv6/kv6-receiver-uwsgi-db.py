import uwsgi
from const import KV6_OK, KV6_SE, KV6_NOK, KV6_NA, KV6_PE, KV6_VERSION, ISO_TIME, KV6_PSHOST
from secret import username, password, sql_username, sql_password, sql_hostname, sql_port, sql_database

import xml.etree.cElementTree as ET
import time
import sys
import sleekxmpp
import zlib
from helpers import stripschema

import monetdb.sql

username += 'test2'

kv6_logging = True
use_KV1 = True

import logging
logging.basicConfig(level=5, format='%(levelname)-8s %(message)s')

xmpp = sleekxmpp.ClientXMPP(username, password)
xmpp.registerPlugin('xep_0060') # PubSub
if xmpp.connect():
    xmpp.process(threaded=True)
else:
    sys.exit(1)

ps = xmpp.plugin["xep_0060"]

connection = monetdb.sql.connect(username=sql_username, password=sql_password, hostname=sql_hostname, port=sql_port, database=sql_database,autocommit=True)
cursor = connection.cursor()

def get_elem_text(message, needle):
    ints = ['journeynumber', 'reinforcementnumber', 'passagesequencenumber', 'vehiclenumber', 'punctuality', 'blockcode', 'numberofcoaches', 'distancesincelastuserstop', 'rd-x', 'rd-y']

    elem = message.find('{http://bison.connekt.nl/tmi8/kv6/msg}'+needle)
    if elem is not None:
        if needle in ints:
            if (needle == 'rd-x' or needle == 'rd-y') and elem.text == '-1':
                return None
            else:
                return int(elem.text)
        elif needle == 'wheelchairaccessible':
            return elem.text == 'ACCESSIBLE'
        else:
            return elem.text
    else:
        return elem

def parseKV6(message, message_type, needles=[]):
    result = {'messagetype': message_type}

    for needle in needles:
        result[needle.replace('-', '_')] = get_elem_text(message, needle)

    # After an END message, it is still possible to receive other messages,
    # such as DEPARTURE. It is good to store that we already received the
    # final message, and therefore may delete this row eventually.
    if message_type == 'END':
        result['Terminated'] = True


    # Since we are receiving messages only once, we are going to do
    # our very best to process everything in a best effort way.
    # If a trip was never send an INIT for, we still want to store it.

    columns = ', '.join(result.keys())
    stubs   = ', '.join(['%('+x+')s' for x in result.keys()])

    if kv6_logging == True:
        cursor.execute('INSERT INTO kv6 ('+ columns +') VALUES (' + stubs + ');', result)

    if use_KV1 == True and message_type in ['ARRIVAL', 'ONSTOP', 'DEPARTURE']:
        # Given that we have a good relationship with the operator, why not enhance some data?
        # KV1 contains the positions of all userstops, we can update our current table with it.
        result['distancesincelastuserstop'] = None
        has_point = (cursor.execute("SELECT locationx_ew, locationy_ns FROM point WHERE pointtype = 'SP' AND pointcode = %(userstopcode)s LIMIT 1;", result) > 0)
        if has_point == True:
            result['rd_x'], result['rd_y'] = cursor.fetchone()


    # For our current table, we are not storing information that comes over END. Nobody should
    # be in such bus anymore. And actually, this information should be cleared reguarly.
    # The reason why we can't do it instant: the protocol allows DEPARTURE to be send after END.
    updatestubs = ', '.join([x+' = %('+x+')s' for x in result.keys()])
    updated = (cursor.execute('UPDATE kv6_current SET ' + updatestubs + ' WHERE journeynumber = %(journeynumber)s AND reinforcementnumber = %(reinforcementnumber)s AND operatingday = %(operatingday)s AND lineplanningnumber = %(lineplanningnumber)s AND dataownercode = %(dataownercode)s;', result) > 0)

    if updated == False:
        columns = ', '.join(result.keys())
        stubs   = ', '.join(['%('+x+')s' for x in result.keys()])
        cursor.execute('INSERT INTO kv6_current ('+ columns +') VALUES (' + stubs + ');', result)

    return

def fetchfrommessage(message):
    message_type = stripschema(message.tag)

    required = ['dataownercode', 'lineplanningnumber', 'operatingday', 'journeynumber', 'reinforcementnumber', 'timestamp', 'source']

    if message_type == 'DELAY':
        return parseKV6(message, message_type, required + ['punctuality'])
    elif message_type == 'INIT':
        return parseKV6(message, message_type, required + ['userstopcode', 'passagesequencenumber', 'vehiclenumber', 'blockcode', 'wheelchairaccessible', 'numberofcoaches'])
    elif message_type in ['ARRIVAL', 'ONSTOP', 'DEPARTURE']:
        return parseKV6(message, message_type, required + ['userstopcode', 'passagesequencenumber', 'vehiclenumber', 'punctuality'])
    elif message_type == 'ONROUTE':
        return parseKV6(message, message_type, required + ['userstopcode', 'passagesequencenumber', 'vehiclenumber', 'punctuality', 'distancesincelastuserstop', 'rd-x', 'rd-y'])
    elif message_type == 'OFFROUTE':
        return parseKV6(message, message_type, required + ['userstopcode', 'passagesequencenumber', 'vehiclenumber', 'rd-x', 'rd-y'])
    elif message_type == 'END':
        return parseKV6(message, message_type, required + ['userstopcode', 'passagesequencenumber', 'vehiclenumber'])

    return False

def reply(xml, start_response):
    start_response('200 OK', [('Content-Type', 'application/xml; charset=utf-8'), ("Content-Length",str(len(xml)))])
    return xml


def KV6posinfo(environ, start_response):
    contents = environ['wsgi.input'].read()
    content_type = environ.get('CONTENT_TYPE')
    if content_type is not None and 'zip' in content_type: # should be: application/x-gzip
        contents = zlib.decompress(contents)

    try:
        xml = ET.fromstring(contents)
    except Exception,e:
        yield reply(KV6_SE % (time.strftime(ISO_TIME), e), start_response)
        return

    if xml.tag == '{http://bison.connekt.nl/tmi8/kv6/msg}VV_TM_PUSH':
        posinfo = xml.findall('{http://bison.connekt.nl/tmi8/kv6/msg}KV6posinfo')
        if len(posinfo) == 0:
            # Heartbeat, het aanleverende systeem zou iedere 300s wat van zich moeten laten horen.
            yield reply(KV6_OK % (time.strftime(ISO_TIME)), start_response)
            return

        else:
            results = []
            for dossier in posinfo:
                for child in dossier.getchildren():
                    if child.tag == '{http://bison.connekt.nl/tmi8/kv6/core}delimiter':
                        pass
                    else:
                        fetchfrommessage(child)
            yield reply(KV6_OK % (time.strftime(ISO_TIME)), start_response)
            return

    elif root.tag == '{http://bison.connekt.nl/tmi8/kv6/msg}VV_TM_RES':
        yield reply(KV6_PE % (time.strftime(ISO_TIME), "What are you thinking? We are the receiver, we don't do responses!"), start_response)
        return

    else:
        yield reply(KV6_NA % (time.strftime(ISO_TIME), "Unknown root tag, did you specify the schema?"), start_response)
        return

uwsgi.applications = {'':KV6posinfo}
