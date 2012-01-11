# import simplejson as serializer
import bson as serializer
import zmq
import sys

use_KV1 = False

context = zmq.Context()
receiver = context.socket(zmq.SUB)
receiver.connect("tcp://127.0.0.1:6006")
receiver.setsockopt(zmq.SUBSCRIBE, '')

while True:
    s = serializer.loads(receiver.recv())
    sys.stdout.write(str(s)+'\n')
    sys.stdout.flush()

