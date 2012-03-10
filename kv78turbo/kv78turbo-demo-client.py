import uwsgi
import zmq

from const import ZMQ_KV78DEMO

def KV78Demo(environ, start_response):
    try:
        timingpointcode = environ['PATH_INFO'][1:]
        if timingpointcode != 'tpc':
            int(timingpointcode)
    except ValueError:
        reply = '[]'
        start_response('404 File Not Found', [('Content-Type', 'application/json'), ('Content-length', str(len(reply)))])
        yield reply
        return

    context = zmq.Context()
    client = context.socket(zmq.REQ)
    client.connect(ZMQ_KV78DEMO)
    client.send(timingpointcode)
    reply = client.recv()
    start_response('200 OK', [('Content-Type', 'application/json'), ('Content-length', str(len(reply)))])
    yield reply
    return

uwsgi.applications = {'': KV78Demo}
