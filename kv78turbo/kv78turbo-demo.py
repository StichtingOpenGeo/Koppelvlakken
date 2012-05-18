import sys
import time
import zmq
import codecs
import csv
from const import ZMQ_KV8, ZMQ_KV78DEMO
from ctx import ctx
from datetime import datetime, timedelta
from gzip import GzipFile
from cStringIO import StringIO

def utf_8_encoder(unicode_csv_data):
    for line in unicode_csv_data:
        yield line.encode('utf-8')

tpc_store = {}
line_store = {}
journey_store = {}

tpc_meta = {}

f = codecs.open('stops.txt', 'r', 'utf-8')
reader = csv.reader(utf_8_encoder(f))
for row in reader:
    try:
        tpc, name, town, x, y = row
        tpc_meta[tpc] = {'Name': name, 'Town': town, 'X': float(x), 'Y': float(y)}
    except:
        pass
f.close()

def toisotime(operationdate, timestamp, row):
    hours, minutes, seconds = timestamp.split(':')
    hours = int(hours)
    if hours >= 48:
        print row

    if hours >= 24:
        deltadays  = hours / 24
        hours = hours % 24
        years, months, days = operationdate.split('-')
        return (datetime(int(years), int(months), int(days), hours, int(minutes), int(seconds)) + timedelta(days = deltadays)).isoformat()
    else:
        return operationdate+'T'+timestamp

def cleanup():
    now = datetime.today() + timedelta(seconds=120)
    for timingpointcode, values in tpc_store.items():
        for journey, row in values.items():
            if now > datetime.strptime(row['ExpectedArrivalTime'], "%Y-%m-%dT%H:%M:%S") and now > datetime.strptime(row['ExpectedDepartureTime'], "%Y-%m-%dT%H:%M:%S"):
                del(tpc_store[timingpointcode][journey])

    for journey_id, values in journey_store.items():
        row = values[max(values.keys())]
        if now > datetime.strptime(row['ExpectedArrivalTime'], "%Y-%m-%dT%H:%M:%S") and now > datetime.strptime(row['ExpectedArrivalTime'], "%Y-%m-%dT%H:%M:%S"):
            line_id = row['DataOwnerCode'] + '_' + row['LinePlanningNumber'] + '_' + row['LineDirection']

            if line_id in line_store and journey_id in line_store[line_id]['Actuals']:
                del(line_store[line_id]['Actuals'][journey_id])

            if journey_id in journey_store:
                del(journey_store[journey_id])

def storecurrect(row):
    id = '_'.join([row['DataOwnerCode'], row['LocalServiceLevelCode'], row['LinePlanningNumber'], row['JourneyNumber'], row['FortifyOrderNumber']])
    line_id = row['DataOwnerCode'] + '_' + row['LinePlanningNumber'] + '_' + row['LineDirection']

    row['ExpectedArrivalTime'] = toisotime(row['OperationDate'], row['ExpectedArrivalTime'], row)
    row['ExpectedDepartureTime'] = toisotime(row['OperationDate'], row['ExpectedDepartureTime'], row)
    
    try:
        for x in ['JourneyNumber', 'FortifyOrderNumber', 'UserStopOrderNumber', 'NumberOfCoaches']:
            if x in row and row[x] is not None and row[x] != 'UNKNOWN':
                row[x] = int(row[x])

        row['IsTimingStop'] = (row['IsTimingStop'] == '1')
    except:
        raise

    if line_id not in line_store:
        line_store[line_id] = { 'DataOwnerCode': row['DataOwnerCode'], 'Network': {}, 'Actuals': {} }
    
    if row['UserStopOrderNumber'] not in line_store[line_id]['Network']:
        line_store[line_id]['Network'][row['UserStopOrderNumber']] = {
            'TimingPointCode': row['TimingPointCode'],
            'IsTimingStop': row['IsTimingStop']
            }
        if row['TimingPointCode'] in tpc_meta:
            line_store[line_id]['Network'][row['UserStopOrderNumber']].update(tpc_meta[row['TimingPointCode']])

    if id not in journey_store:
        journey_store[id] = {row['UserStopOrderNumber']: row}
    else:
        journey_store[id][row['UserStopOrderNumber']] = row

    if row['TripStopStatus'] in set(['ARRIVED', 'PASSED']): # , 'DRIVING']): Driving alleen nemen als kleinste waarde uit lijn, gegeven dat er geen ARRIVED/PASSED is
        for key in journey_store[id].keys():
            if key < row['UserStopOrderNumber']:
                del(journey_store[id][key])

        if row['JourneyStopType'] == 'LAST':
            if id in line_store[line_id]['Actuals']:
                del line_store[line_id]['Actuals'][id]
        else:
            line_store[line_id]['Actuals'][id] = row

    if row['TimingPointCode'] not in tpc_store:
        tpc_store[row['TimingPointCode']] = {id: row}
    else:
        tpc_store[row['TimingPointCode']][id] = row


context = zmq.Context()

client = context.socket(zmq.REP)
client.bind(ZMQ_KV78DEMO)

kv8 = context.socket(zmq.SUB)
#kv8.connect(ZMQ_KV8)
#kv8.setsockopt(zmq.SUBSCRIBE, '')

kv8.connect("tcp://83.98.158.170:7817")
kv8.setsockopt(zmq.SUBSCRIBE, "/GOVI/KV8")


poller = zmq.Poller()
poller.register(client, zmq.POLLIN)
poller.register(kv8, zmq.POLLIN)

garbage = 0

while True:
    socks = dict(poller.poll())
    
    if socks.get(kv8) == zmq.POLLIN:
        multipart = kv8.recv_multipart()
        content = GzipFile('','r',0,StringIO(''.join(multipart[1:]))).read()
        c = ctx(content)
        if 'DATEDPASSTIME' in c.ctx:
            for row in c.ctx['DATEDPASSTIME'].rows():
                storecurrect(row)
            sys.stdout.write('8')
            sys.stdout.flush()
        else:
            sys.stdout.write('.')
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
                    reply[line] = len(values['Actuals'])
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
                #print reply.keys()                            
                client.send_json(reply)
                sys.stdout.flush()

        else:
            client.send_json([])

    if garbage > 120:
        cleanup()
        sys.stdout.write('c')
        sys.stdout.flush()
        garbage = 0
    else:
        garbage += 1
