import uwsgi
import zmq
import re

from consts import ZMQ_SERVER, ZMQ_PUBSUB_GOVI, ZMQ_PUBSUB_ARRIVA, REQUEST_TIMEOUT, KV55_ERROR

def KV55(environ, start_response):
    try:
        request = environ['PATH_INFO'][1:]
        source, timingpointcode = request.split('/')
        int(timingpointcode)
    except ValueError:
        reply = KV55_ERROR % {'timingpointcode': request, 'error': 'Invalid TimingPointCode'}
        start_response('404 File Not Found', [('Content-Type', 'text/xml'), ('Content-length', str(len(reply)))])
        yield reply
        return

    context = zmq.Context()
    client = context.socket(zmq.REQ)
    client.connect(ZMQ_SERVER)

    receiver = context.socket(zmq.SUB)

    if source == 'kv55':
        receiver.connect(ZMQ_PUBSUB_GOVI)
    elif source == 'arriva':
        receiver.connect(ZMQ_PUBSUB_ARRIVA)
    else:
        reply = KV55_ERROR % {'timingpointcode': request, 'error': 'Invalid Source'}
        start_response('404 File Not Found', [('Content-Type', 'text/xml'), ('Content-length', str(len(reply)))])
        yield reply
        return

    receiver.setsockopt(zmq.SUBSCRIBE, timingpointcode+',')
    poller = zmq.Poller()
    poller.register(client, zmq.POLLIN)
    poller.register(receiver, zmq.POLLIN)

    client.send(request)

    while True:
        socks = dict(poller.poll(REQUEST_TIMEOUT))

        if socks.get(client) == zmq.POLLIN:
            reply = client.recv()
            if reply != 'WAIT':
                start_response('200 OK', [('Content-Type', 'text/xml'), ('Content-length', str(len(reply)))])
                yield reply
                return

        elif socks.get(receiver) == zmq.POLLIN:
            result = receiver.recv()
            _timingpointcode, reply = result.split(',', 1)
            start_response('200 OK', [('Content-Type', 'text/xml'), ('Content-length', str(len(reply)))])
            yield reply
            return

        else:
            reply = KV55_ERROR % {'timingpointcode': timingpointcode, 'error': 'Timeout'}
            start_response('504 Gateway Timeout', [('Content-Type', 'text/xml'), ('Content-length', str(len(reply)))])
            yield reply
            return

uwsgi.applications = {'': KV55}
