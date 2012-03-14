import sys
import time
import zmq
from const import ZMQ_KV7KALENDER, ZMQ_KV7PLANNING, ZMQ_KV8

context = zmq.Context()

kv7kalender = context.socket(zmq.SUB)
kv7kalender.connect(ZMQ_KV7KALENDER)
kv7kalender.setsockopt(zmq.SUBSCRIBE, '')

kv7planning = context.socket(zmq.SUB)
kv7planning.connect(ZMQ_KV7PLANNING)
kv7planning.setsockopt(zmq.SUBSCRIBE, '')

kv8 = context.socket(zmq.SUB)
kv8.connect(ZMQ_KV8)
kv8.setsockopt(zmq.SUBSCRIBE, '')

poller = zmq.Poller()
poller.register(kv7planning, zmq.POLLIN)
poller.register(kv7kalender, zmq.POLLIN)
poller.register(kv8, zmq.POLLIN)

while True:
    socks = dict(poller.poll())
    now = time.time()

    if socks.get(kv8) == zmq.POLLIN:
        f = open('/tmp/KV8/'+str(now), 'w')
        f.write(kv8.recv())
        f.close()
        sys.stdout.write('8')
        sys.stdout.flush()

    elif socks.get(kv7planning) == zmq.POLLIN:
        f = open('/home/projects/openov/kv7/htdocs/KV7planning/'+str(int(now)), 'w')
        f.write(kv7planning.recv())
        f.close()
        sys.stdout.write('p')
        sys.stdout.flush()

    elif socks.get(kv7kalender) == zmq.POLLIN:
        f = open('/home/projects/openov/kv7/htdocs/KV7kalender/'+str(int(now)), 'w')
        f.write(kv7kalender.recv())
        f.close()
        sys.stdout.write('k')
        sys.stdout.flush()
