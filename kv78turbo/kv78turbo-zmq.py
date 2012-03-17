import zmq
import sys
from const import ZMQ_KV7KALENDER, ZMQ_KV7PLANNING, ZMQ_KV8, ZMQ_KV78

context = zmq.Context()

kv7kalender = context.socket(zmq.PUB)
kv7kalender.bind(ZMQ_KV7KALENDER)

kv7planning = context.socket(zmq.PUB)
kv7planning.bind(ZMQ_KV7PLANNING)

kv8 = context.socket(zmq.PUB)
kv8.bind(ZMQ_KV8)

kv78 = context.socket(zmq.PULL)
kv78.bind(ZMQ_KV78)

while True:
    content = kv78.recv()
    sys.stdout.write(content[0])
    sys.stdout.flush()

    if content[0] == '8':
        kv8.send(content[1:])

    elif content[0] == 'p':
        kv7planning.send(content[1:])

    elif content[0] == 'k':
        kv7kalender.send(content[1:])
