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

def get_elem_list(message, needle):
    elem = message.findall('{http://bison.connekt.nl/tmi8/kv15/msg}'+needle)
    return set([x.text for x in elem])

def get_elem_text(message, needle):
    ints = ['messagecodenumber', 'reasontype', 'effecttype', 'measuretype', 'advisetype']

    elem = message.find('{http://bison.connekt.nl/tmi8/kv15/msg}'+needle)
    if elem is not None:
        if needle in ints:
            return int(elem.text)
        else:
            return elem.text
    else:
        return elem

def parseKV15(message, message_type, needles=[]):
    result = {'messagetype': message_type}

    for needle in needles:
        result[needle] = get_elem_text(message, needle)

    # Since we are receiving messages only once, we are going to do
    # our very best to process everything in a best effort way.
    # If a trip was never send an INIT for, we still want to store it.

    if message_type == 'DELETEMESSAGE':
        if kv15_logging == True:
            columns = ', '.join(result.keys() + ['lineplanningnumber', 'userstopcodes'])
            stubs   = ', '.join(['%('+x+')s' for x in result.keys() + ['lineplanningnumber', 'userstopcodes']])
            cursor.execute('INSERT INTO kv15_deletemessage ('+ columns +') VALUES (' + stubs + ');', result)

        # Because ON DELETE CASCADE is used, we don't have to bother about the other two tables!
        cursor.execute('DELETE FROM kv15_current WHERE messagecodenumber = %(messagecodenumber)s AND messagecodedate = %(messagecodedate)s AND dataownercode = %(dataownercode)s;', result)
    
    elif message_type == 'STOPMESSAGE':
        userstopcodes = get_elem_list(message, 'userstopcode')
        lineplanningnumbers = get_elem_list(message, 'lineplaninngnumbers')

        if kv15_logging == True:
            columns = ', '.join(result.keys() + ['lineplanningnumber', 'userstopcodes'])
            stubs   = ', '.join(['%('+x+')s' for x in result.keys() + ['lineplanningnumber', 'userstopcodes']])
            cursor.execute('INSERT INTO kv15 ('+ columns +') VALUES (' + stubs + ');', result + [','.join(userstopcodes), ','.join(lineplanningnumbers)])

        updatestubs = ', '.join([x+' = %('+x+')s' for x in result.keys()])
        updated = (cursor.execute('UPDATE kv15_current SET ' + updatestubs + ' WHERE messagecodenumber = %(messagecodenumber)s AND messagecodedate = %(messagecodedate)s AND dataownercode = %(dataownercode)s;', result) > 0)
        if updated == True:
            cursor.execute('SELECT userstopcode, messageid FROM kv15_userstopcode, kv15_current WHERE kv15_current.messageid = kv15_userstopcode.messageid AND messagecodenumber = %(messagecodenumber)s AND messagecodedate = %(messagecodedate)s AND dataownercode = %(dataownercode)s;', result)
            rows = cursor.fetchall()
            messageid = rows[0][1]
            old_userstopcodes = set([row[0] for row in rows])
            
            new_userstopcodes = userstopcodes - old_userstopcodes
            removed_userstopcodes = old_userstopcodes - userstopcodes

            if len(new_userstopcodes) > 0:
                toinsert = [(messageid, userstopcode) for userstopcode in new_userstopcodes]
                cursor.executemany('INSERT INTO kv15_userstopcode (messageid, userstopcode) VALUES (%s, %s);', toinsert)

            if len(removed_userstopcodes) > 0:
                instubs = ', '.join(['%s' for x in range(0, len(removed_userstopcodes))])
                cursor.execute('DELETE FROM kv15_userstopcode WHERE messageid = %s AND userstopcode IN (' + instubs + ');', [messageid] + list(removed_userstopcodes))

            cursor.execute('SELECT lineplanningnumber, messageid FROM kv15_lineplanningnumber, kv15_current WHERE kv15_current.messageid = kv15_lineplanningnumber.messageid AND messagecodenumber = %(messagecodenumber)s AND messagecodedate = %(messagecodedate)s AND dataownercode = %(dataownercode)s;', result)
            rows = cursor.fetchall()
            messageid = rows[0][1]
            old_lineplanningnumbers = set([row[0] for row in rows])
            
            new_lineplanningnumbers = lineplanningnumbers - old_lineplanningnumbers
            removed_lineplanningnumbers = old_lineplanningnumbers - lineplanningnumbers

            if len(new_lineplanningnumbers) > 0:
                toinsert = [(messageid, lineplanningnumber) for lineplanningnumber in new_lineplanningnumbers]
                cursor.executemany('INSERT INTO kv15_lineplanningnumber (messageid, lineplanningnumber) VALUES (%s, %s);', toinsert)

            if len(removed_lineplanningnumbers) > 0:
                instubs = ', '.join(['%s' for x in range(0, len(removed_lineplanningnumbers))])
                cursor.execute('DELETE FROM kv15_lineplanningnumber WHERE messageid = %s AND lineplanningnumber IN (' + instubs + ');', [messageid] + list(removed_lineplanningnumbers))

        else:
            columns = ', '.join(result.keys())
            stubs   = ', '.join(['%('+x+')s' for x in result.keys()])
            cursor.execute('INSERT INTO kv15_current ('+ columns +') VALUES (' + stubs + ');', result)

            toinsert = [(messageid, userstopcode) for userstopcode in userstopcodes]
            cursor.executemany('INSERT INTO kv15_userstopcode (messageid, userstopcode) VALUES (%s, %s);', toinsert)

            toinsert = [(messageid, lineplanningnumber) for lineplanningnumber in lineplanningnumbers]
            cursor.executemany('INSERT INTO kv15_lineplanningnumber (messageid, lineplanningnumber) VALUES (%s, %s);', toinsert)

    return

def fetchfrommessage(message):
    message_type = stripschema(message.tag)

    required = ['dataownercode', 'messagecodedate', 'messagecodenumber']

    if message_type == 'STOPMESSAGE':
        return parseKV15(message, message_type, required + ['messagepriority', 'messagetype', 'messagetypeduration', 'messagestarttime', 'messagesendtime', 'messagecontent', 'reasontype', 'subreasontype', 'reasoncontent', 'effecttype', 'subeffecttype', 'effectcontent', 'measuretype', 'submeasuretype', 'measurecontent', 'advicetype', 'subadvicetype', 'advicecontent', 'messagetimestamp'])
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
