import uwsgi
from const import KV6_OK, KV6_SE, KV6_NOK, KV6_NA, KV6_PE, KV6_VERSION, ISO_TIME, PS_PUSH

import xml.etree.cElementTree as ET
from helpers import stripschema

import time
import sys
import zlib
import StringIO
import gzip
import zmq
import simplejson as serializer
#import bson as serializer

context = zmq.Context()
sender = context.socket(zmq.PUSH)
sender.connect(PS_PUSH)

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

    return result


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

    return None

def reply(xml, start_response):
    start_response('200 OK', [('Content-Type', 'application/xml; charset=utf-8'), ("Content-Length",str(len(xml)))])
    return xml


def KV6posinfo(environ, start_response):
    global sender
    contents = None
    content_type = environ.get('CONTENT_TYPE')
    if content_type is not None and 'zip' in content_type: # should be: application/x-gzip
	f = StringIO.StringIO(environ['wsgi.input'].read())
	f.write(contents)
	f.seek(0)
	contents = gzip.GzipFile(filename=None, fileobj=f, mode='rb').read()
    else:
    	contents = environ['wsgi.input'].read()

    try:
        xml = ET.fromstring(contents)
    except Exception,e:
	sender.send_multipart(["9292/error/KV6posinfo", str(e)])

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
                    if child.tag != '{http://bison.connekt.nl/tmi8/kv6/core}delimiter':
                        result = fetchfrommessage(child)
                        if result is not None:
                            results.append(result)

            sender.send_multipart(["9292/KV6posinfo", serializer.dumps(results)])
            # sender.send(serializer.dumps(results))
            # sys.stdout.write('.')
            # sys.stdout.flush()

            yield reply(KV6_OK % (time.strftime(ISO_TIME)), start_response)
            return

    elif root.tag == '{http://bison.connekt.nl/tmi8/kv6/msg}VV_TM_RES':
        yield reply(KV6_PE % (time.strftime(ISO_TIME), "What are you thinking? We are the receiver, we don't do responses!"), start_response)
        return

    else:
        yield reply(KV6_NA % (time.strftime(ISO_TIME), "Unknown root tag, did you specify the schema?"), start_response)
        return

uwsgi.applications = {'':KV6posinfo}
