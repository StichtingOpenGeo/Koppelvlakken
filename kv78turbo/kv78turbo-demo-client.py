import uwsgi
import zmq

from const import ZMQ_KV78DEMO

def notfound():
    start_response('404 File Not Found', [('Content-Type', 'application/json'), ('Content-length', '2')])
    yield '[]'

def KV78Demo(environ, start_response):
    url = environ['PATH_INFO'][1:]
    arguments = url.split('/')
    if arguments[0] not in set(['tpc', 'journey', 'line']) or len(arguments) > 2:
         return notfound()

    context = zmq.Context()
    client = context.socket(zmq.REQ)
    client.connect(ZMQ_KV78DEMO)
    client.send(url)
    reply = client.recv()
    if len(reply) == 0:
        return notfound()
        
    start_response('200 OK', [('Content-Type', 'application/json'), ('Content-length', str(len(reply)))])
    return reply

uwsgi.applications = {'': KV78Demo}
