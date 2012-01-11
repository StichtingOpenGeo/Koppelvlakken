import monetdb.sql
# import simplejson as serializer
import bson as serializer
import zmq
import sys

from secret import username, password, sql_username, sql_password, sql_hostname, sql_port, sql_database

use_KV1 = False

connection = monetdb.sql.connect(username=sql_username, password=sql_password, hostname=sql_hostname, port=sql_port, database=sql_database, autocommit=True)
cursor = connection.cursor()

context = zmq.Context()
receiver = context.socket(zmq.SUB)
receiver.connect("tcp://127.0.0.1:6006")
receiver.setsockopt(zmq.SUBSCRIBE, '')

while True:
    s = receiver.recv()
    sys.stdout.write('.')
    sys.stdout.flush()
    result = serializer.loads(s)
    message_type = result['messagetype']

    if use_KV1 == True and message_type in ['ARRIVAL', 'ONSTOP', 'DEPARTURE']:
        # Given that we have a good relationship with the operator, why not enhance some data?
        # KV1 contains the positions of all userstops, we can update our current table with it.
        result['distancesincelastuserstop'] = None
        has_point = (cursor.execute("SELECT locationx_ew, locationy_ns FROM point WHERE pointtype = 'SP' AND pointcode = %(userstopcode)s LIMIT 1;", result) > 0)
        if has_point == True:
            result['rd_x'], result['rd_y'] = cursor.fetchone()

    # After an END message, it is still possible to receive other messages,
    # such as DEPARTURE. It is good to store that we already received the
    # final message, and therefore may delete this row eventually.
    if message_type == 'END':
        result['Terminated'] = True
    elif message_type == 'INIT':
    	result['Terminated'] = False

    # For our current table, we are not storing information that comes over END. Nobody should
    # be in such bus anymore. And actually, this information should be cleared reguarly.
    # The reason why we can't do it instant: the protocol allows DEPARTURE to be send after END.
    updatestubs = ', '.join([x+' = %('+x+')s' for x in result.keys()])
    updated = (cursor.execute('UPDATE kv6_current SET ' + updatestubs + ' WHERE journeynumber = %(journeynumber)s AND reinforcementnumber = %(reinforcementnumber)s AND operatingday = %(operatingday)s AND lineplanningnumber = %(lineplanningnumber)s AND dataownercode = %(dataownercode)s;', result) > 0)

    if updated == False:
        columns = ', '.join(result.keys())
        stubs   = ', '.join(['%('+x+')s' for x in result.keys()])
        cursor.execute('INSERT INTO kv6_current ('+ columns +') VALUES (' + stubs + ');', result)

