import time
import zmq
import sys
from datetime import datetime, timedelta
from email.utils import parsedate
from httplib2 import Http
from BeautifulSoup import BeautifulSoup
from multiprocessing import Process

from consts import ZMQ_ARRIVA, ZMQ_PUBSUB_ARRIVA, ARRIVA_REALTIME_URL, KV55_REP, KV55_TRIP

# The "worker" functions listen on a zeromq PULL connection for "work" 
# (numbers to be processed) from the ventilator, square those numbers,
# and send the results down another zeromq PUSH connection to the 
# results manager.

def _parse_http_datetime(date):
    return datetime(*parsedate(date)[:6])

def _parse_arriva_content(request_timestamp, send_timestamp, tpc, content):
    trips = ''
    soup = BeautifulSoup(content)
    operdate = soup.find('input', {"id": "realtime-date"})['value']
    operdate = datetime.strptime(operdate, "%d-%m-%Y").date()

    realtime = soup.find('table', {"id": "realtime-table"})
    if realtime is not None:
        prev = 0
        for row in realtime.findAll('tr')[1:]:
            items = row.findAll('td')
            try:
                [linenumber, linename] = items[0].text[5:].split(' naar ')
            except:
                linenumber = '0'
                linename = items[0].text
                pass

            try:
                target = items[1].text+':00'
                expected = items[2].text
            except:
                return

            now = int(target.split(':')[0])
            if prev > now:
                operdate = operdate + timedelta(days = 1)

            prev = now

            if expected == '-':
                expected = target
                tripstatus = 'PLANNED'
            else:
                expected += ':00'
                tripstatus = 'DRIVING'

            trips += KV55_TRIP % {'operdate': operdate,
                                  'linenumber': linenumber,
                                  'linename': linename, 'target': target,
                                  'expected': expected,
                                  'journeynumber': 0, 'fortifyordernumber': 0,
                                  'tripstopstatus': tripstatus }

        soup = None
        response = KV55_REP % \
               {'request': request_timestamp,
                'sent': send_timestamp.strftime("%Y-%m-%dT%H:%M:%S+02:00"),
                'tpc': tpc, 'trips': trips, 'sequencenumber': 0 }

        return response.encode('UTF-8')

def worker(wrk_num):
    # Initialize a zeromq context
    context = zmq.Context()

    # Set up a channel to receive work from the ventilator
    work_receiver = context.socket(zmq.PULL)
    work_receiver.connect(ZMQ_ARRIVA)

    # Set up a channel to send result of work to the results reporter
    results_sender = context.socket(zmq.PUSH)
    results_sender.connect("tcp://127.0.0.1:5558")

    # Set up a channel to receive control messages over
    control_receiver = context.socket(zmq.SUB)
    control_receiver.connect("tcp://127.0.0.1:5559")
    control_receiver.setsockopt(zmq.SUBSCRIBE, "")

    # Set up a poller to multiplex the work receiver and control receiver channels
    poller = zmq.Poller()
    poller.register(work_receiver, zmq.POLLIN)
    poller.register(control_receiver, zmq.POLLIN)

    # Setup HTTP downloader
    http = Http(timeout=10)
    headers = {'Connection': 'close'}

    # Loop and accept messages from both channels, acting accordingly
    while True:
        socks = dict(poller.poll())

        # If the message came from work_receiver channel, square the number
        # and send the answer to the results reporter
        if socks.get(work_receiver) == zmq.POLLIN:
            timingpointcode = work_receiver.recv()
            sys.stdout.write('.')
            sys.stdout.flush()

            try:
                request_timestamp = time.strftime("%Y-%m-%dT%H:%M:%S+02:00", time.gmtime())
                url = ARRIVA_REALTIME_URL % timingpointcode
                response, content = http.request(url, 'GET', headers=headers)
            except Exception, e:
                results_sender.send('FAIL,'+timingpointcode)
            
            send_timestamp = _parse_http_datetime(response['date'])
            parsed = _parse_arriva_content(request_timestamp, send_timestamp, timingpointcode, content)
            if parsed is not None:
                results_sender.send(timingpointcode+','+parsed)
                sys.stdout.write('+')
                sys.stdout.flush()

            results_sender.send('FAIL,'+timingpointcode)

        # If the message came over the control channel, shut down the worker.
        elif socks.get(control_receiver) == zmq.POLLIN:
            control_message = control_receiver.recv()
            if control_message == "FINISHED":
                print("Worker %i received FINSHED, quitting!" % wrk_num)
                break

# The "results_manager" function receives each result from multiple workers,
# and prints those results.  When all results have been received, it signals
# the worker processes to shut down.

def result_manager():
    # Initialize a zeromq context
    context = zmq.Context()
    
    # Set up a channel to receive results
    results_receiver = context.socket(zmq.PULL)
    results_receiver.bind("tcp://127.0.0.1:5558")

    # Set up a channel to send control commands
    control_sender = context.socket(zmq.PUB)
    control_sender.bind("tcp://127.0.0.1:5559")

    # Set up a channel to send result messages
    sender = context.socket(zmq.PUB)
    sender.bind(ZMQ_PUBSUB_ARRIVA)

    while True:
        sender.send(results_receiver.recv())

    # Signal to all workers that we are finished
    control_sender.send("FINISHED")
    time.sleep(5)

if __name__ == "__main__":
    # Create a pool of workers to distribute work to
    worker_pool = range(16)
    for wrk_num in range(len(worker_pool)):
        Process(target=worker, args=(wrk_num,)).start()

    # Fire up our result manager...
    result_manager = Process(target=result_manager, args=())
    result_manager.start()
