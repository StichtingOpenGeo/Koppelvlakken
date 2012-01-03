import uwsgi
from const import KV17_OK, KV17_SE, KV17_NOK, KV17_NA, KV17_PE, KV17_VERSION, ISO_TIME, KV17_PSHOST
from secret import username, password, sql_username, sql_password, sql_hostname, sql_port, sql_database

import xml.etree.cElementTree as ET
import time
import sys
import sleekxmpp
import zlib
from helpers import stripschema, reply

import monetdb.sql

kv17_logging = True
"""
import logging
logging.basicConfig(level=5, format='%(levelname)-8s %(message)s')

xmpp = sleekxmpp.ClientXMPP(username, password)
xmpp.registerPlugin('xep_0060') # PubSub
if xmpp.connect():
    xmpp.process(threaded=True)
else:
    sys.exit(1)

ps = xmpp.plugin["xep_0060"]
"""
connection = monetdb.sql.connect(username=sql_username, password=sql_password, hostname=sql_hostname, port=sql_port, database=sql_database,autocommit=True)
cursor = connection.cursor()

def get_elem_text(message, needle):
    ints = ['journeynumber', 'reinforcementnumber', 'reasontype', 'advicetype', 'passagesequencenumber', 'lagtime']

    elem = message.find('{http://bison.connekt.nl/tmi8/kv17/msg}'+needle)
    if elem is not None:
        if needle in ints:
            return int(elem.text)
        else:
            return elem.text
    else:
        return elem

def parseKV17(message, message_type, needles=[]):
    result = {'messagetype': message_type}

    for needle in needles:
        result[needle] = get_elem_text(message, needle)

    if kv17_logging == True:
        columns = ', '.join(result.keys())
        stubs   = ', '.join(['%('+x+')s' for x in result.keys()])
        cursor.execute('INSERT INTO kv17 ('+ columns +') VALUES (' + stubs + ');', result)

    return

def fetchfrommessage(message):
    message_type = stripschema(message.tag)

    required = ['dataownercode', 'lineplanningnumber', 'operatingday', 'journeynumber', 'reinforcementnumber', 'timestamp']

    if message_type == 'CANCEL':
        return parseKV17(message, message_type, required + ['reasontype', 'subreasontype', 'reasoncontent', 'advicetype', 'subadvicetype', 'advicecontent'])
    elif message_type == 'MUTATIONMESSAGE':
        return parseKV17(message, message_type, required + ['userstopcode', 'passagesequencenumber', 'reasontype', 'subreasontype', 'reasoncontent', 'advicetype', 'subadvicetype', 'advicecontent'])
    elif message_type == 'SHORTEN':
        return parseKV17(message, message_type, required + ['userstopcode', 'passagesequencenumber'])
    elif message_type == 'LAG':
        return parseKV17(message, message_type, required + ['userstopcode', 'passagesequencenumber', 'lagtime'])
    elif message_type == 'CHANGEPASSTIMES':
        return parseKV17(message, message_type, required + ['userstopcode', 'passagesequencenumber', 'targetarrivaltime', 'targetdeparturetime', 'journeystoptype'])
    elif message_type == 'CHANGEDESTINATION':
        return parseKV17(message, message_type, required + ['userstopcode', 'passagesequencenumber', 'destinationcode', 'destinationname50', 'destinationname16', 'destinationdetail16', 'destinationdisplay16'])
    elif message_type in ['RECOVER', 'ADD']:
        return parseKV17(message, message_type, required)

    return False

def KV17messages(environ, start_response):
    contents = environ['wsgi.input'].read()
    content_type = environ.get('CONTENT_TYPE')
    if content_type is not None and 'zip' in content_type: # should be: application/x-gzip
        contents = zlib.decompress(contents)

    try:
        xml = ET.fromstring(contents)
    except Exception,e:
        yield reply(KV17_SE % (time.strftime(ISO_TIME), e), start_response)
        return

    if xml.tag == '{http://bison.connekt.nl/tmi8/kv17/msg}VV_TM_PUSH':
        posinfo = xml.findall('{http://bison.connekt.nl/tmi8/kv17/msg}KV17cvlinfo')
        if posinfo is not None:
            results = []
            for dossier in posinfo:
                for child in dossier.getchildren():
                    if child.tag == '{http://bison.connekt.nl/tmi8/kv17/core}delimiter':
                        pass
                    else:
                        fetchfrommessage(child)
            yield reply(KV17_OK % (time.strftime(ISO_TIME)), start_response)
            return

    elif root.tag == '{http://bison.connekt.nl/tmi8/kv17/msg}VV_TM_RES':
        yield reply(KV17_PE % (time.strftime(ISO_TIME), "What are you thinking? We are the receiver, we don't do responses!"), start_response)
        return

    else:
        yield reply(KV17_NA % (time.strftime(ISO_TIME), "Unknown root tag, did you specify the schema?"), start_response)
        return

uwsgi.applications = {'':KV17cvlinfo}
