import zmq
import sys
from time import gmtime, strftime, time
from httplib2 import Http
from xml.etree.cElementTree import XML

from consts import ZMQ_SERVER, ZMQ_PUBSUB, KV55_REQ, GOVI_KV55_URL

queue = {}
sequencenumber = 0

context = zmq.Context()
receiver = context.socket(zmq.SUB)
receiver.connect(ZMQ_PUBSUB)
receiver.setsockopt(zmq.SUBSCRIBE, '')

client = context.socket(zmq.REP)
client.bind(ZMQ_SERVER)

poller = zmq.Poller()
poller.register(client, zmq.POLLIN)
poller.register(receiver, zmq.POLLIN)

while True:
    socks = dict(poller.poll())
    now = int(time())

    # We received a client with a TimingPointCode
    if socks.get(client) == zmq.POLLIN:
        timingpointcode = client.recv()

        # Giving that we do not have this TimingPointCode
        # in our queue, request it...
        if timingpointcode not in queue:
            client.send('WAIT')
            sys.stdout.write('.')
            sys.stdout.flush()

            sequencenumber += 1

            xml = KV55_REQ % {'timestamp': strftime("%Y-%m-%dT%H:%M:%S", gmtime()),
                              'sequencenumber': sequencenumber,
                              'timingpointcode': timingpointcode}

            headers = {'Content-type': 'text/xml', 'Content-length': str(len(xml))}
            
            try:
                response, content = Http().request(GOVI_KV55_URL, 'POST', headers=http_headers, body=xml)
                queue[timingpointcode] = {'timestamp': now}
            except:
                pass

        # On the other hand, we might have a cached
        # result, send it to the client
        elif 'XML' in queue[timingpointcode]:
            client.send(queue[timingpointcode]['XML'])
            sys.stdout.write('c')
            sys.stdout.flush()

    # We received a PubSub message and store the result
    elif socks.get(receiver) == zmq.POLLIN:
        result = receiver.recv()
        try:
            timingpointcode, result = result.split(',', 1)
            if timingpointcode not in queue:
                queue[timingpointcode] = {'timestamp': now}

            queue[timingpointcode]['XML'] = result
            sys.stdout.write('s')
            sys.stdout.flush()
        except ValueError:
            pass

    # Cleanup our internal cache
    history = now - 60
    for timingpointcode, storage in queue.items():
        if history > storage['timestamp']:
            del(queue[timingpointcode])
