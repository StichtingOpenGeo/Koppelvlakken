import uwsgi
from const import KV15_OK, KV15_SE, KV15_NOK, KV15_NA, KV15_PE, KV15_VERSION, ISO_TIME, KV15_PSHOST
from secret import username, password, sql_username, sql_password, sql_hostname, sql_port, sql_database

import xml.etree.cElementTree as ET
from helpers import stripschema, reply

import time
import sys
import zlib
import zmq
# import simplejson as serializer
import bson as serializer

context = zmq.Context()
sender = context.socket(zmq.PUB)
sender.bind("tcp://*:6015")

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
    result = {'messagetype': message_type }

    for needle in needles:
        result[needle] = get_elem_text(message, needle)

    if message_type == 'STOPMESSAGE':
        result['userstopcodes'] = get_elem_list(message, 'userstopcode')
        result['lineplanningnumbers'] = get_elem_list(message, 'lineplaninngnumber')

    sender.send(serializer.dumps(result))
    sys.stdout.write('.')
    sys.stdout.flush()
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
