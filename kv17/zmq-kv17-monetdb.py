import monetdb.sql
# import simplejson as serializer
import bson as serializer
import zmq
import sys

from secret import username, password, sql_username, sql_password, sql_hostname, sql_port, sql_database

connection = monetdb.sql.connect(username=sql_username, password=sql_password, hostname=sql_hostname, port=sql_port, database=sql_database,autocommit=True)
cursor = connection.cursor()

context = zmq.Context()
receiver = context.socket(zmq.SUB)
receiver.connect("tcp://127.0.0.1:6017")
receiver.setsockopt(zmq.SUBSCRIBE, '')

while True:
    s = receiver.recv()
    sys.stdout.write('.')
    sys.stdout.flush()
    result = serializer.loads(s)
    message_type = result['messagetype']

    columns = ', '.join(result.keys())
    stubs   = ', '.join(['%('+x+')s' for x in result.keys()])
    cursor.execute('INSERT INTO kv17 ('+ columns +') VALUES (' + stubs + ');', result)
