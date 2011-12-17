import uwsgi
from const import KV6_OK, KV6_SE, KV6_NOK, KV6_NA, KV6_PE, KV6_VERSION, ISO_TIME, KV6_PSHOST
from secret import username, password

import xml.etree.cElementTree as ET
import time
import sys
import sleekxmpp
from StringIO import StringIO
from zipfile import ZipFile
from helpers import stripschema

import logging
logging.basicConfig(level=5, format='%(levelname)-8s %(message)s')

xmpp = sleekxmpp.ClientXMPP(username, password)
xmpp.registerPlugin('xep_0060') # PubSub
if xmpp.connect():
    xmpp.process(threaded=True)
else:
    sys.exit(1)

ps = xmpp.plugin["xep_0060"]

def reply(xml, start_response):
    start_response('200 OK', [('Content-Type', 'application/xml; charset=utf-8'), ("Content-Length",str(len(xml)))])
    return xml


def KV6posinfo(environ, start_response):
    try:
        contents = environ['wsgi.input'].read()
        zf = ZipFile(StringIO(contents))
        filename = zf.namelist()[0]
        f = zf.open(filename)
        contents = f.read()
        f.close()
        zf.close()
    except Exception,e:
        yield reply(KV6_PE % (time.strftime(ISO_TIME), e), start_response)

    try:
        xml = ET.fromstring(contents)
    except Exception,e:
        yield reply(KV6_SE % (time.strftime(ISO_TIME), e))

    if xml.tag == '{http://bison.connekt.nl/tmi8/kv6/msg}VV_TM_PUSH':
        posinfo = xml.findall('{http://bison.connekt.nl/tmi8/kv6/msg}KV6posinfo')
        if len(posinfo) == 0:
            # Heartbeat, het aanleverende systeem zou iedere 300s wat van zich moeten laten horen.
            yield reply(KV6_OK % (time.strftime(ISO_TIME)), start_response)

        else:
            for dossier in posinfo:
                for child in dossier.getchildren():
                    if child.tag == '{http://bison.connekt.nl/tmi8/kv6/core}delimiter':
                        pass
                    else:
                        dataowner = child.find('{http://bison.connekt.nl/tmi8/kv6/msg}dataownercode')
                        journeynumber = child.find('{http://bison.connekt.nl/tmi8/kv6/msg}journeynumber')
                        reinforcementnumber = child.find('{http://bison.connekt.nl/tmi8/kv6/msg}journeynumber')

                        if dataowner is not None and journeynumber is not None and reinforcementnumber is not None:
                            # Als je de standaard letterlijk leest zijn de volgende velden verplicht:
                            # DataOwnerCode, LinePlanningNumber, OperatingDay, JourneyNumber, ReinforcementNumber
                            node  = '%s/%s' % (dataowner.text, journeynumber.text)
                            state = stripschema(child.tag)
                            if state == 'INIT':
                                try:
                                    ps.create_node(KV6_PSHOST, node)
                                except:
                                    pass

                            try:
                                ps.publish(KV6_PSHOST, node, id=reinforcementnumber.text, payload=child)
                            except:
                                pass

                            print '%s/%s|%s - %s' % (dataowner.text, journeynumber.text, reinforcementnumber.text, stripschema(child.tag))

            yield reply(KV6_OK % (time.strftime(ISO_TIME)), start_response)

    elif root.tag == '{http://bison.connekt.nl/tmi8/kv6/msg}VV_TM_RES':
        yield reply(KV6_PE % (time.strftime(ISO_TIME), "What are you thinking? We are the receiver, we don't do responses!"), start_response)

    else:
        yield reply(KV6_NA % (time.strftime(ISO_TIME), "Unknown root tag, did you specify the schema?"), start_response)

uwsgi.applications = {'':KV6posinfo}
