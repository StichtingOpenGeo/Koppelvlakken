import zmq
import sys
from urllib3 import HTTPConnectionPool
from gzip import GzipFile
from time import time

if len(sys.argv) != 3 or len(sys.argv[2].split(':')) != 2:
    print 'usage: tcp://pubsub-server:port host:port'
    sys.exit(1)

context = zmq.Context()
sub = context.socket(zmq.SUB)
sub.connect(sys.argv[1])
sub.setsockopt(zmq.SUBSCRIBE, '')

host,port = sys.argv[2].split(':')
pool = HTTPConnectionPool(host,port=int(port),maxsize=4)

while True:
    multipart = sub.recv_multipart()
    path = multipart[0]
    content = ''.join(multipart[1:])
    try:
        r = pool.urlopen('POST',path,headers={'Content-Type':'application/gzip','Connection':'Keep-Alive','User-Agent' : 'ZMQ2http 0.1'},body=content,release_conn=True)
        print str(r.status) + ' ' + str(len(content))
        if r.status != 200:
           #Debug errors
           print r.data
           f = open("%.4f" % time() + '.gz', 'wb') 
           f.write(''.join(multipart[1:]))
           f.close()
    except Exception as e:
        print e
        pass
