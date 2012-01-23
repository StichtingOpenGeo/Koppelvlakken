import uwsgi
import zmq
import re

from consts import ZMQ_SERVER, ZMQ_PUBSUB, REQUEST_TIMEOUT, KV55_REP

def KV55(environ, start_response):
    timingpointcode = environ['PATH_INFO'][1:]
    try:
        int(timingpointcode)
    except ValueError:
        reply = KV55_REP % {'timingpointcode': timingpointcode, 'error': 'Invalid TimingPointCode'}
        start_response('404 File Not Found', [('Content-Type', 'text/xml'), ('Content-length', str(len(reply)))])
        yield reply
        return

    context = zmq.Context()
    
    receiver = context.socket(zmq.SUB)
    receiver.connect(ZMQ_PUBSUB)
    receiver.setsockopt(zmq.SUBSCRIBE, timingpointcode+',')

    client = context.socket(zmq.REQ)
    client.connect(ZMQ_SERVER)

    poller = zmq.Poller()
    poller.register(client, zmq.POLLIN)
    poller.register(receiver, zmq.POLLIN)

    client.send(timingpointcode)

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
            reply = KV55_REP % {'timingpointcode': timingpointcode, 'error': 'Timeout'}
            start_response('504 Gateway Timeout', [('Content-Type', 'text/xml'), ('Content-length', str(len(reply)))])
            yield reply
            return

uwsgi.applications = {'': KV55}
