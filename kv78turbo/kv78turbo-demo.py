import sys
import time
import zmq
from const import ZMQ_KV8, ZMQ_KV78DEMO
from ctx import ctx
from datetime import datetime, timedelta

tpc_store = {}
line_store = {}
journey_store = {}

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
    now = datetime.today() + timedelta(seconds=120)
    for timingpointcode, values in tpc_store.items():
        for journey, row in values.items():
            if now > datetime.strptime(row['ExpectedDepartureTime'], "%Y-%m-%dT%H:%M:%S"):
                del(tpc_store[timingpointcode][journey])
                
def storecurrect(row):
    id = '_'.join([row['DataOwnerCode'], row['OperationDate'], row['LinePlanningNumber'], row['JourneyNumber']])

    row['ExpectedArrivalTime'] = toisotime(row['OperationDate'], row['ExpectedArrivalTime'])
    row['ExpectedDepartureTime'] = toisotime(row['OperationDate'], row['ExpectedDepartureTime'])
    
    try:
        for x in ['JourneyNumber', 'FortifyOrderNumber', 'UserStopOrderNumber', 'NumberOfCoaches']:
            if x in row:
                row[x] = int(row[x])

        row['IsTimingStop'] = (row['IsTimingStop'] == '1')
    except:
        raise

    if id not in journey_store:
        journey_store[id] = {row['UserStopOrderNumber']: row}
    else:
        journey_store[id][row['UserStopOrderNumber']] = row

    if row['TripStopStatus'] in set(['ARRIVED', 'PASSED']):
        for key in journey_store[id].keys():
            if key < row['UserStopOrderNumber']:
                del(journey_store[id][key])

        line_id = row['DataOwnerCode'] + '_' + row['LinePlanningNumber']
        if row['JourneyStopType'] == 'LAST':
            if line_id in line_store and id in line_store[line_id]:
                del line_store[line_id][id]
        else:
            if line_id not in line_store:
                line_store[line_id] = {id: row}
            else:
                line_store[line_id][id] = row

    if row['TimingPointCode'] not in tpc_store:
        tpc_store[row['TimingPointCode']] = {id: row}
    else:
        tpc_store[row['TimingPointCode']][id] = row


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
    socks = dict(poller.poll(120000))
    
    if socks.get(kv8) == zmq.POLLIN:
        content = kv8.recv()
        c = ctx(content)
        for row in c.ctx['DATEDPASSTIME'].rows():
            storecurrect(row)
        sys.stdout.write('8')
        sys.stdout.flush()

    elif socks.get(client) == zmq.POLLIN:
        url = client.recv()
        arguments = url.split('/')

        if arguments[0] == 'tpc':
            if len(arguments) == 1:
                reply = {}
                for tpc, values in tpc_store.items():
                    reply[tpc] = len(values)
                client.send_json(reply)
                sys.stdout.write('t')
                sys.stdout.flush()
            else:
                reply = {}
                for tpc in set(arguments[1].split(',')):
                    if tpc in tpc_store:
                        if tpc != '':
                            reply[tpc] = tpc_store[tpc]
                            sys.stdout.write('T')
                client.send_json(reply)
                sys.stdout.flush()
        
        elif arguments[0] == 'journey':
            if len(arguments) == 1:
                reply = {}
                for journey, values in journey_store.items():
                    reply[journey] = len(values)
                client.send_json(reply)
                sys.stdout.write('j')
                sys.stdout.flush()
            else:
                reply = {}
                for journey in set(arguments[1].split(',')):
                    if journey in journey_store:
                        if journey != '':
                            reply[journey] = journey_store[journey]
                            sys.stdout.write('J')
                client.send_json(reply)
                sys.stdout.flush()
        
        elif arguments[0] == 'line':
            if len(arguments) == 1:
                reply = {}
                for line, values in line_store.items():
                    reply[line] = len(values)
                client.send_json(reply)
                sys.stdout.write('l')
                sys.stdout.flush()
            else:
                reply = {}
                for line in set(arguments[1].split(',')):
                    if line in line_store:
                        if line != '':
                            reply[line] = line_store[line]
                            sys.stdout.write('L')
                client.send_json(reply)
                sys.stdout.flush()

        else:
            client.send_json([])

    else:
        cleanup()
        sys.stdout.write('c')
        sys.stdout.flush()
