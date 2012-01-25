import zmq
import sys
from time import gmtime, strftime, time
from httplib2 import Http
from xml.etree.cElementTree import XML

from consts import ZMQ_SERVER, ZMQ_PUBSUB_GOVI, ZMQ_PUBSUB_ARRIVA, ZMQ_ARRIVA, KV55_REQ, GOVI_KV55_URL, CLEANUP_TIMEOUT

queue = {}
sequencenumber = 0

context = zmq.Context()
receiver_govi = context.socket(zmq.SUB)
receiver_govi.connect(ZMQ_PUBSUB_GOVI)
receiver_govi.setsockopt(zmq.SUBSCRIBE, '')

receiver_arriva = context.socket(zmq.SUB)
receiver_arriva.connect(ZMQ_PUBSUB_ARRIVA)
receiver_arriva.setsockopt(zmq.SUBSCRIBE, '')

arriva = context.socket(zmq.PUSH)
arriva.bind(ZMQ_ARRIVA)

client = context.socket(zmq.REP)
client.bind(ZMQ_SERVER)

poller = zmq.Poller()
poller.register(client, zmq.POLLIN)
poller.register(receiver_govi, zmq.POLLIN)
poller.register(receiver_arriva, zmq.POLLIN)

http = Http()

def govi_send(timingpointcode):
        global sequencenumber
        sequencenumber += 1

        xml = KV55_REQ % {'timestamp': strftime("%Y-%m-%dT%H:%M:%S", gmtime()),
                          'sequencenumber': sequencenumber,
                          'timingpointcode': timingpointcode}

        http_headers = {'Content-type': 'text/xml', 'Content-length': str(len(xml))}
        response, content = http.request(GOVI_KV55_URL, 'POST', headers=http_headers, body=xml)

# We received a PubSub message and store the result
def cache_reply(receiver, source):
    result = receiver.recv()
    try:
        timingpointcode, result = result.split(',', 1)
        uri = source + '/' + timingpointcode
        if source not in queue:
            queue[uri] = {'timestamp': now}

        queue[uri]['XML'] = result
    except ValueError:
        pass

while True:
    socks = dict(poller.poll(CLEANUP_TIMEOUT))
    now = int(time())

    # We received a client with a TimingPointCode
    if socks.get(client) == zmq.POLLIN:
        uri = client.recv()
        source, timingpointcode = uri.split('/')

        # Giving that we do not have this TimingPointCode
        # in our queue, request it...
        if uri not in queue:
            client.send('WAIT')
            queue[uri] = {'timestamp': now}
            if source == 'kv55':
                sys.stdout.write('g')
                sys.stdout.flush()
                govi_send(timingpointcode)
   
            elif source == 'arriva':
                sys.stdout.write('a')
                sys.stdout.flush()
                arriva.send(timingpointcode)

        # On the other hand, we might have a cached
        # result, send it to the client
        elif 'XML' in queue[uri]:
            client.send(queue[uri]['XML'])
            sys.stdout.write('c')
            sys.stdout.flush()

        # Still queued
        else:
            client.send('WAIT')

    # We received a PubSub message and store the result
    elif socks.get(receiver_govi) == zmq.POLLIN:
        cache_reply(receiver_govi, 'kv55')
        sys.stdout.write('G')
        sys.stdout.flush()
    elif socks.get(receiver_arriva) == zmq.POLLIN:
        cache_reply(receiver_arriva, 'arriva')
        sys.stdout.write('A')
        sys.stdout.flush()

    # Cleanup our internal cache
    history = now - 60
    for uri, storage in queue.items():
        if history > storage['timestamp']:
            del(queue[uri])
