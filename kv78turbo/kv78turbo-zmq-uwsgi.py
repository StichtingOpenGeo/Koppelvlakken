import uwsgi
from gzip import GzipFile
from cStringIO import StringIO
import zmq
from const import ZMQ_KV78, GOVI_KV78_SERVER

context = zmq.Context()

kv78 = context.socket(zmq.PUSH)
kv78.connect(ZMQ_KV78)

def KV78turbo(environ, start_response):
    if environ['REMOTE_ADDR'] not in [GOVI_KV78_SERVER]:
        start_response('403 Forbidden', [('Content-Type','text/plain')])
        return 'Je mag hier niet komen.'

    if environ['REQUEST_URI'] in ['/KV8', '/KV7planning', '/KV7kalender']:
        try:
            contents = environ['wsgi.input'].read()
            
            if contents == '':
                start_response('204 No content', [('Content-Type','text/plain')])
                return

            contents = GzipFile('','r',0,StringIO(contents)).read()
        except Exception,e:
            print e
            start_response('500 Internal Server Error', [('Content-Type','text/plain')])
            return e
        
        """
        if environ['REQUEST_URI'] == '/KV8':
            kv78.send('8' + contents)
        elif environ['REQUEST_URI'] == '/KV7planning':
            kv78.send('p' + contents)
        elif environ['REQUEST_URI'] == '/KV7kalender':
            kv78.send('k' + contents)
        """

        if len(environ['REQUEST_URI']) > 4:
            kv78.send(environ['REQUEST_URI'][4] + contents)
        else:
            kv78.send('8' + contents)

        start_response('200 OK', [('Content-Type','text/plain')])
        return

    start_response('404 Not Found', [('Content-Type','text/plain')])
    return

uwsgi.applications = {'':KV78turbo}
