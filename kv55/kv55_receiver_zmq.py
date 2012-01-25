import uwsgi
import zmq
import re
from time import gmtime, strftime

from consts import KV55_RES, ZMQ_PUBSUB_GOVI

context = zmq.Context()
sender = context.socket(zmq.PUB)
sender.bind(ZMQ_PUBSUB_GOVI)

match_timingpointcode = re.compile('<TimingPointCode>([0-9]+)</TimingPointCode>')

def KV55(environ, start_response):
    try:
        #response = environ['wsgi.input'].read()
        response = environ['wsgi.input'].read(int(environ['CONTENT_LENGTH']))
        timingpointcode = match_timingpointcode.search(response).group(1)
        response = response.replace('<Request>',"<License>http://openov.nl/license/GOVI-1.0-TravelInfo</License>\n\t<Request>")

        sender.send('%(timingpointcode)s,%(response)s' % {'timingpointcode': timingpointcode, 'response': response})
    except SyntaxError:
        pass

    reply = KV55_RES % {'timestamp': strftime("%Y-%m-%dT%H:%M:%S", gmtime())}
    start_response('200 OK', [('Content-Type', 'text/xml'), ('Content-length', str(len(reply)))])
    yield reply

uwsgi.applications = {'':KV55}
