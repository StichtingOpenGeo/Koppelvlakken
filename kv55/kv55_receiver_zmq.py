import uwsgi
import zmq
from time import gmtime, strftime
from xml.etree.cElementTree import XML

from consts import KV55_RES, ZMQ_PUBSUB

context = zmq.Context()
sender = context.socket(zmq.PUB)
sender.bind(ZMQ_PUBSUB)

def KV55(environ, start_response):
    reply = KV55_RES % {'timestamp': strftime("%Y-%m-%dT%H:%M:%S", gmtime())}
    start_response('200 OK', [('Content-Type', 'text/xml'), ('Content-length', str(len(reply)))])
    
    try:
        response = environ['wsgi.input'].read(int(environ['CONTENT_LENGTH']))
        #response = environ['wsgi.input'].read()
        root = XML(response)
        timingpointcode = root.find('.//TimingPointCode').text

        sender.send('%(timingpointcode)s,%(response)s' % {'timingpointcode': timingpointcode, 'response': response})
    except SyntaxError:
        pass

    yield reply

uwsgi.applications = {'':KV55}
