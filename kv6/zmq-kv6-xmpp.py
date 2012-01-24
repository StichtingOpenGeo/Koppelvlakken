import simplejson as serializer
# import bson as serializer
import zmq
import sys

context = zmq.Context()
receiver = context.socket(zmq.SUB)
receiver.connect("tcp://127.0.0.1:6006")
receiver.setsockopt(zmq.SUBSCRIBE, '')

while True:
    results = serializer.loads(receiver.recv())
    for result in results:
        sys.stdout.write(str(result)+'\n')
        sys.stdout.flush()

