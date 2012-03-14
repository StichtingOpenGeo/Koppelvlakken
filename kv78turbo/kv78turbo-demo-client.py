import uwsgi
import zmq

from const import ZMQ_KV78DEMO

COMMON_HEADERS = [('Content-Type', 'application/json'), ('Access-Control-Allow-Origin', '*'), ('Access-Control-Allow-Headers', 'Requested-With,Content-Type')]

def notfound(start_response):
    start_response('404 File Not Found', COMMON_HEADERS + [('Content-length', '2')])
    yield '[]'

def KV78Demo(environ, start_response):
    url = environ['PATH_INFO'][1:]
    if len(url) > 0 and url[-1] == '/':
        url = url[:-1]
        
    arguments = url.split('/')
    if arguments[0] not in set(['tpc', 'journey', 'line']) or len(arguments) > 2:
         return notfound(start_response)

    context = zmq.Context()
    client = context.socket(zmq.REQ)
    client.connect(ZMQ_KV78DEMO)
    client.send(url)
    reply = client.recv()
    if len(reply) == 0:
        return notfound(start_response)
        
    start_response('200 OK', COMMON_HEADERS + [('Content-length', str(len(reply)))])
    return reply

uwsgi.applications = {'': KV78Demo}
