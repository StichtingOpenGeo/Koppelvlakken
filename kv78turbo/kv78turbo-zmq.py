import uwsgi
from gzip import GzipFile
from cStringIO import StringIO
import zmq
from const import ZMQ_KV7KALENDER, ZMQ_KV7PLANNING, ZMQ_KV8

context = zmq.Context()

kv7kalender = context.socket(zmq.PUB)
kv7kalender.bind(ZMQ_KV7KALENDER)

kv7planning = context.socket(zmq.PUB)
kv7planning.bind(ZMQ_KV7PLANNING)

kv8 = context.socket(zmq.PUB)
kv8.bind(ZMQ_KV8)

def KV78turbo(environ, start_response):
    contents = environ['wsgi.input'].read()
    contents = GzipFile('','r',0,StringIO(contents)).read()

    if environ['REQUEST_URI'] == '/KV8':
        kv8.send(contents)
    
    elif environ['REQUEST_URI'] == '/KV7planning':
        kv7planning.send(contents)

    elif environ['REQUEST_URI'] == '/KV7kalender':
        kv7kalender.send(contents)

    else:
        start_response('404 Not Found', [('Content-Type','text/plain')])
        return

    start_response('200 OK', [('Content-Type','text/plain')])
    return


uwsgi.applications = {'':KV78turbo}
