import uwsgi
from const import KV15_OK, KV15_SE, KV15_NOK, KV15_NA, KV15_PE, KV15_VERSION, ISO_TIME, KV15_PSHOST
from secret import username, password, sql_username, sql_password, sql_hostname, sql_port, sql_database

import xml.etree.cElementTree as ET
import time
import sys
import sleekxmpp
import zlib
from helpers import stripschema, reply

import monetdb.sql

kv15_logging = True
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

def get_elem_list(message, needle):
    elem = message.findall('.//{http://bison.connekt.nl/tmi8/kv15/msg}'+needle)
    return set([x.text for x in elem])

def get_elem_text(message, needle):
    ints = ['messagecodenumber', 'reasontype', 'effecttype', 'measuretype', 'advicetype']

    elem = message.find('{http://bison.connekt.nl/tmi8/kv15/msg}'+needle)
    if elem is not None:
        if needle in ints:
            return int(elem.text)
        else:
            return elem.text
    else:
        return elem

def parseKV15(message, message_type, needles=[]):
    result = {}

    for needle in needles:
        result[needle] = get_elem_text(message, needle)

    # Since we are receiving messages only once, we are going to do
    # our very best to process everything in a best effort way.
    # If a trip was never send an INIT for, we still want to store it.

    if message_type == 'DELETEMESSAGE':
        if kv15_logging == True:
            columns = ', '.join(result.keys())
            stubs   = ', '.join(['%('+x+')s' for x in result.keys()])
            cursor.execute('INSERT INTO kv15_deletemessage ('+ columns +') VALUES (' + stubs + ');', result)

        cursor.execute('DELETE FROM kv15_current WHERE messagecodenumber = %(messagecodenumber)s AND messagecodedate = %(messagecodedate)s AND dataownercode = %(dataownercode)s;', result)
        cursor.execute('DELETE FROM kv15_userstopcode WHERE messagecodenumber = %(messagecodenumber)s AND messagecodedate = %(messagecodedate)s AND dataownercode = %(dataownercode)s;', result)
        cursor.execute('DELETE FROM kv15_lineplanningnumber WHERE messagecodenumber = %(messagecodenumber)s AND messagecodedate = %(messagecodedate)s AND dataownercode = %(dataownercode)s;', result)
    
    elif message_type == 'STOPMESSAGE':
        userstopcodes = get_elem_list(message, 'userstopcode')
        lineplanningnumbers = get_elem_list(message, 'lineplaningnumber')

        if kv15_logging == True:
            tmp_columns = result.keys() + ['lineplanningnumbers', 'userstopcodes']
            tmp_content = {'userstopcodes': ','.join(userstopcodes), 'lineplanningnumbers': ','.join(lineplanningnumbers)}
            tmp_content.update(result)

            columns = ', '.join(tmp_columns)
            stubs   = ', '.join(['%('+x+')s' for x in tmp_columns])
            cursor.execute('INSERT INTO kv15_stopmessage ('+ columns +') VALUES (' + stubs + ');', tmp_content)

        updatestubs = ', '.join([x+' = %('+x+')s' for x in result.keys()])
        updated = (cursor.execute('UPDATE kv15_current SET ' + updatestubs + ' WHERE messagecodenumber = %(messagecodenumber)s AND messagecodedate = %(messagecodedate)s AND dataownercode = %(dataownercode)s;', result) > 0)
        if updated == True:
            num_userstopcodes = cursor.execute('SELECT kv15_userstopcode.userstopcode FROM kv15_userstopcode WHERE messagecodenumber = %(messagecodenumber)s AND messagecodedate = %(messagecodedate)s AND dataownercode = %(dataownercode)s;', result)
            rows = cursor.fetchall()
            old_userstopcodes = set([row[0] for row in rows])
            
            new_userstopcodes = userstopcodes - old_userstopcodes
            removed_userstopcodes = old_userstopcodes - userstopcodes

            if len(new_userstopcodes) > 0:
                toinsert = [(result['dataownercode'], result['messagecodedate'], result['messagecodenumber'], userstopcode) for userstopcode in new_userstopcodes]
                cursor.executemany('INSERT INTO kv15_userstopcode (dataownercode, messagecodedate, messagecodenumber, userstopcode) VALUES (%s, %s, %s, %s);', toinsert)

            if len(removed_userstopcodes) > 0:
                instubs = ', '.join(['%s' for x in range(0, len(removed_userstopcodes))])
                cursor.execute('DELETE FROM kv15_userstopcode WHERE messagecodenumber = %s AND messagecodedate = %s AND dataownercode = %s AND userstopcode IN (' + instubs + ');', [result['messagecodenumber'], result['messagecodedate'], result['dataownercode']] + list(removed_userstopcodes))


            num_lineplanningnumbers = cursor.execute('SELECT kv15_lineplanningnumber.lineplanningnumber FROM kv15_lineplanningnumber WHERE messagecodenumber = %(messagecodenumber)s AND messagecodedate = %(messagecodedate)s AND dataownercode = %(dataownercode)s;', result)
            rows = cursor.fetchall()
            old_lineplanningnumbers = set([row[0] for row in rows])
            
            new_lineplanningnumbers = lineplanningnumbers - old_lineplanningnumbers
            removed_lineplanningnumbers = old_lineplanningnumbers - lineplanningnumbers

            if len(new_lineplanningnumbers) > 0:
                toinsert = [(result['dataownercode'], result['messagecodedate'], result['messagecodenumber'], lineplanningnumber) for lineplanningnumber in new_lineplanningnumbers]
                cursor.executemany('INSERT INTO kv15_lineplanningnumber (dataownercode, messagecodedate, messagecodenumber, lineplanningnumber) VALUES (%s, %s, %s, %s);', toinsert)

            if len(removed_lineplanningnumbers) > 0:
                instubs = ', '.join(['%s' for x in range(0, len(removed_lineplanningnumbers))])
                cursor.execute('DELETE FROM kv15_lineplanningnumber WHERE messagecodenumber = %s AND messagecodedate = %s AND dataownercode = %s AND lineplanningnumber IN (' + instubs + ');', [result['messagecodenumber'], result['messagecodedate'], result['dataownercode']] + list(removed_lineplanningnumbers))

        else:
            columns = ', '.join(result.keys())
            stubs   = ', '.join(['%('+x+')s' for x in result.keys()])
            cursor.execute('INSERT INTO kv15_current ('+ columns +') VALUES (' + stubs + ');', result)
            
            if len(userstopcodes) > 0:
                toinsert = [(result['dataownercode'], result['messagecodedate'], result['messagecodenumber'], userstopcode) for userstopcode in userstopcodes]
                cursor.executemany('INSERT INTO kv15_userstopcode (dataownercode, messagecodedate, messagecodenumber, userstopcode) VALUES (%s, %s, %s, %s);', toinsert)
            if len(lineplanningnumbers) > 0:
                toinsert = [(result['dataownercode'], result['messagecodedate'], result['messagecodenumber'], lineplanningnumber) for lineplanningnumber in lineplanningnumbers]
                cursor.executemany('INSERT INTO kv15_lineplanningnumber (dataownercode, messagecodedate, messagecodenumber, lineplanningnumber) VALUES (%s, %s, %s, %s);', toinsert)

    return

def fetchfrommessage(message):
    message_type = stripschema(message.tag)

    required = ['dataownercode', 'messagecodedate', 'messagecodenumber']

    if message_type == 'STOPMESSAGE':
        return parseKV15(message, message_type, required + ['messagepriority', 'messagetype', 'messagedurationtype', 'messagestarttime', 'messageendtime', 'messagecontent', 'reasontype', 'subreasontype', 'reasoncontent', 'effecttype', 'subeffecttype', 'effectcontent', 'measuretype', 'submeasuretype', 'measurecontent', 'advicetype', 'subadvicetype', 'advicecontent', 'messagetimestamp'])
    elif message_type == 'DELETEMESSAGE':
        return parseKV15(message, message_type, required)

    return False

def KV15messages(environ, start_response):
    contents = environ['wsgi.input'].read()
    content_type = environ.get('CONTENT_TYPE')
    if content_type is not None and 'zip' in content_type: # should be: application/x-gzip
        contents = zlib.decompress(contents)

    try:
        xml = ET.fromstring(contents)
    except Exception,e:
        yield reply(KV15_SE % (time.strftime(ISO_TIME), e), start_response)
        return

    if xml.tag == '{http://bison.connekt.nl/tmi8/kv15/msg}VV_TM_PUSH':
        posinfo = xml.findall('{http://bison.connekt.nl/tmi8/kv15/msg}KV15messages')
        if posinfo is not None:
            results = []
            for dossier in posinfo:
                for child in dossier.getchildren():
                    if child.tag == '{http://bison.connekt.nl/tmi8/kv15/core}delimiter':
                        pass
                    else:
                        fetchfrommessage(child)
            yield reply(KV15_OK % (time.strftime(ISO_TIME)), start_response)
            return

    elif root.tag == '{http://bison.connekt.nl/tmi8/kv15/msg}VV_TM_RES':
        yield reply(KV15_PE % (time.strftime(ISO_TIME), "What are you thinking? We are the receiver, we don't do responses!"), start_response)
        return

    else:
        yield reply(KV15_NA % (time.strftime(ISO_TIME), "Unknown root tag, did you specify the schema?"), start_response)
        return

uwsgi.applications = {'':KV15messages}
