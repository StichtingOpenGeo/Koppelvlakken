import uwsgi
from const import KV17_OK, KV17_SE, KV17_NOK, KV17_NA, KV17_PE, KV17_VERSION, ISO_TIME, KV17_PSHOST
from secret import username, password, sql_username, sql_password, sql_hostname, sql_port, sql_database

import xml.etree.cElementTree as ET
import time
import sys
import zlib
import zmq
from helpers import stripschema, reply

# import simplejson as serializer
import bson as serializer

context = zmq.Context()
sender = context.socket(zmq.PUB)
sender.bind("tcp://*:6017")

def get_elem_text(message, needle):
    ints = ['journeynumber', 'reinforcementnumber', 'reasontype', 'advicetype', 'passagesequencenumber', 'lagtime']

    elem = message.find('.//{http://bison.connekt.nl/tmi8/kv17/msg}'+needle)
    if elem is not None:
        if needle in ints:
            return int(elem.text)
        else:
            return elem.text
    else:
        return elem

def parseKV17(message, message_type, journey, needles=[]):
    result = {'messagetype': message_type}
    result.update(journey)

    for needle in needles:
        result[needle] = get_elem_text(message, needle)

    sender.send(serializer.dumps(result))

    sys.stdout.write('.')
    sys.stdout.flush()

    return

def fetchfrommessage(message):
    journey = {}
    journey_xml = message.find('{http://bison.connekt.nl/tmi8/kv17/msg}KV17JOURNEY')
    for needle in ['dataownercode', 'lineplanningnumber', 'operatingday', 'journeynumber', 'reinforcementnumber']:
        journey[needle] = get_elem_text(journey_xml, needle)
 
    for child in message.getchildren():
        parent_type = stripschema(child.tag)
        if parent_type == 'KV17MUTATEJOURNEY':
            required = ['timestamp']
            for subchild in child.getchildren():
                message_type = stripschema(subchild.tag)
                if message_type in ['RECOVER', 'ADD']:
                    parseKV17(message, message_type, journey, required)
                elif message_type == 'CANCEL':
                    parseKV17(message, message_type, journey, required + ['reasontype', 'subreasontype', 'reasoncontent', 'advicetype', 'subadvicetype', 'advicecontent'])

        elif parent_type == 'KV17MUTATEJOURNEYSTOP':
            required = ['timestamp', 'userstopcode', 'passagesequencenumber']
            for subchild in child.getchildren():
                message_type = stripschema(subchild.tag)
                if message_type == 'MUTATIONMESSAGE':
                    parseKV17(message, message_type, journey, required + ['reasontype', 'subreasontype', 'reasoncontent', 'advicetype', 'subadvicetype', 'advicecontent'])
                elif message_type == 'SHORTEN':
                    parseKV17(message, message_type, journey, required)
                elif message_type == 'LAG':
                    parseKV17(message, message_type, journey, required + ['lagtime'])
                elif message_type == 'CHANGEPASSTIMES':
                    parseKV17(message, message_type, journey, required + ['targetarrivaltime', 'targetdeparturetime', 'journeystoptype'])
                elif message_type == 'CHANGEDESTINATION':
                    parseKV17(message, message_type, journey, required + ['destinationcode', 'destinationname50', 'destinationname16', 'destinationdetail16', 'destinationdisplay16'])

    return False

def KV17cvlinfo(environ, start_response):
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
            for dossier in posinfo:
                fetchfrommessage(dossier)
            
            yield reply(KV17_OK % (time.strftime(ISO_TIME)), start_response)
            return

    elif root.tag == '{http://bison.connekt.nl/tmi8/kv17/msg}VV_TM_RES':
        yield reply(KV17_PE % (time.strftime(ISO_TIME), "What are you thinking? We are the receiver, we don't do responses!"), start_response)
        return

    else:
        yield reply(KV17_NA % (time.strftime(ISO_TIME), "Unknown root tag, did you specify the schema?"), start_response)
        return

uwsgi.applications = {'':KV17cvlinfo}
