import sys
import time
import zmq
from const import ZMQ_KV8, ZMQ_KV78DEMO
from ctx import ctx
from datetime import datetime, timedelta

store = {}

def toisotime(operationdate, timestamp):
    hours, minutes, seconds = timestamp.split(':')
    hours = int(hours)
    if hours >= 24:
        hours -= 24
        years, months, days = operationdate.split('-')
        return (datetime(int(years), int(months), int(days), hours, int(minutes), int(seconds)) + timedelta(days = 1)).isoformat()
    else:
        return operationdate+'T'+timestamp

def cleanup():
    now = datetime.today()
    for timingpointcode, values in store.items():
        for journey, row in values.items():
            if now > datetime.strptime(row['ExpectedDepartureTime'], "%Y-%m-%dT%H:%M:%S"):
                del(store[timingpointcode][journey])
                

def storecurrect(row):
    id = '_'.join([row['DataOwnerCode'], row['OperationDate'], row['LinePlanningNumber'], row['JourneyNumber']])

    row['ExpectedArrivalTime'] = toisotime(row['OperationDate'], row['ExpectedArrivalTime'])
    row['ExpectedDepartureTime'] = toisotime(row['OperationDate'], row['ExpectedDepartureTime'])

    if row['TimingPointCode'] not in store:
        store[row['TimingPointCode']] = {id: row}
    else:
        store[row['TimingPointCode']][id] = row

context = zmq.Context()

client = context.socket(zmq.REP)
client.bind(ZMQ_KV78DEMO)

kv8 = context.socket(zmq.SUB)
kv8.connect(ZMQ_KV8)
kv8.setsockopt(zmq.SUBSCRIBE, '')

poller = zmq.Poller()
poller.register(client, zmq.POLLIN)
poller.register(kv8, zmq.POLLIN)


while True:
    socks = dict(poller.poll(120))
    
    if socks.get(kv8) == zmq.POLLIN:
        content = kv8.recv()
        c = ctx(content)
        for row in c.ctx['DATEDPASSTIME'].rows():
            storecurrect(row)
        sys.stdout.write('8')
        sys.stdout.flush()

    elif socks.get(client) == zmq.POLLIN:
        tpc = client.recv()
        if tpc == 'tpc':
            reply = {}
            for tpc, values in store.items():
                reply[tpc] = len(values)
            client.send_json(reply)
            sys.stdout.write('t')
            sys.stdout.flush()
        else:
            if tpc in store:
                client.send_json(store[tpc])
                sys.stdout.write('s')
                sys.stdout.flush()
            else:
                client.send_json([])
                sys.stdout.write('_')
                sys.stdout.flush()
    else:
        cleanup()
