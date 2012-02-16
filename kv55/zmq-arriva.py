import zmq
import sys
import time
from datetime import datetime, timedelta
from email.utils import parsedate
from httplib2 import Http
from BeautifulSoup import BeautifulSoup
from consts import ZMQ_ARRIVA, ZMQ_PUBSUB_ARRIVA, ARRIVA_REALTIME_URL, KV55_REP, KV55_TRIP
from threading import Thread
import gc

context = zmq.Context()
receiver = context.socket(zmq.PULL)
receiver.connect(ZMQ_ARRIVA)

sender = context.socket(zmq.PUB)
sender.bind(ZMQ_PUBSUB_ARRIVA)


class Arriva(Thread):
    def __init__ (self, timingpointcode):
        Thread.__init__(self)
        self.http = Http(timeout=30)
        self.daemon = True
        self.timingpointcode = timingpointcode

    def _parse_http_datetime(self, date):
        try:
            return datetime(*parsedate(date)[:6])
        except:
            return None

    def _parse_arriva_content(self, request_timestamp, send_timestamp, tpc, content):
        trips = ''
        soup = BeautifulSoup(content)

        realtime = soup.find('table', {"id": "realtime-table"})
        if realtime is not None:
            operdate = soup.find('input', {"id": "realtime-date"})['value']
            operdate = datetime.strptime(operdate, "%d-%m-%Y").date()
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
                    target = items[1].text
                    expected = items[2].text
                except:
                    print row
                    continue;

                now = int(target.split(':')[0])
                if prev > now:
                    operdate = operdate + timedelta(days = 1)

                prev = now

                if expected == '-':
                    expected = ''

                trips += KV55_TRIP % {'operdate': operdate, 'linenumber': linenumber,
                                      'linename': linename, 'target': target, 'expected': expected}

            soup = None
            response = KV55_REP \
                    % {'request': request_timestamp,
                       'sent': send_timestamp.strftime("%Y-%m-%dT%H:%M:%S+0200"),
                       'tpc': tpc, 'trips': trips}

            return response.encode('UTF-8')

    def run(self):
        try:
            request_timestamp = time.strftime("%Y-%m-%dT%H:%M:%S+0200", time.gmtime())
            headers = {'Connection': 'close'}
            url = ARRIVA_REALTIME_URL % self.timingpointcode
            response, content = self.http.request(url, 'GET', headers=headers)
            self.http = None
        except Exception, e:
            return

        if 'date' in response:
            send_timestamp = self._parse_http_datetime(response['date'])
            if send_timestamp is not None:
                parsed = self._parse_arriva_content(request_timestamp, send_timestamp, self.timingpointcode, content)
                if parsed is not None:
                    sender.send(self.timingpointcode+','+parsed)
                    sys.stdout.write('+')
                    sys.stdout.flush()

        return

while True:
    timingpointcode = receiver.recv()
    Arriva(timingpointcode).start()
    sys.stdout.write('.')
    sys.stdout.flush()
    gc.collect()
