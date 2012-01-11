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
receiver.connect("tcp://127.0.0.1:6015")
receiver.setsockopt(zmq.SUBSCRIBE, '')

while True:
    s = receiver.recv()
    sys.stdout.write('.')
    sys.stdout.flush()
    result = serializer.loads(s)
    message_type = result['messagetype']

    if message_type == 'DELETEMESSAGE':
        cursor.execute('DELETE FROM kv15_current WHERE messagecodenumber = %(messagecodenumber)s AND messagecodedate = %(messagecodedate)s AND dataownercode = %(dataownercode)s;', result)
        cursor.execute('DELETE FROM kv15_userstopcode WHERE messagecodenumber = %(messagecodenumber)s AND messagecodedate = %(messagecodedate)s AND dataownercode = %(dataownercode)s;', result)
        cursor.execute('DELETE FROM kv15_lineplanningnumber WHERE messagecodenumber = %(messagecodenumber)s AND messagecodedate = %(messagecodedate)s AND dataownercode = %(dataownercode)s;', result)
    
    elif message_type == 'STOPMESSAGE':
        userstopcodes = result['userstopcodes']
        lineplanningnumbers = result['lineplanningnumbers']

        del(result['userstopcodes'])
        del(result['lineplanningnumbers'])

        updatestubs = ', '.join([x+' = %('+x+')s' for x in result.keys()])
        updated = (cursor.execute('UPDATE kv15_current SET ' + updatestubs + ' WHERE messagecodenumber = %(messagecodenumber)s AND messagecodedate = %(messagecodedate)s AND dataownercode = %(dataownercode)s;', result) > 0)
        if updated == True:

            num_userstopcodes = cursor.execute('SELECT kv15_userstopcode.userstopcode FROM kv15_userstopcode WHERE messagecodenumber = %(messagecodenumber)s AND messagecodedate = %(messagecodedate)s AND dataownercode = %(dataownercode)s;', result)
            rows = cursor.fetchall()
            old_userstopcodes = set([row[0] for row in rows])
            
            new_userstopcodes = userstopcodes - old_userstopcodes
            removed_userstopcodes = old_userstopcodes - userstopcodes

            if len(new_userstopcodes) > 0:
                toinsert = [(result['dataownercode'], result['messagecodedate'], result['messagecodenumber'], userstopcode) for userstopcode in new_userstopcodes]
                cursor.executemany('INSERT INTO kv15_userstopcode (dataownercode, messagecodedate, messagecodenumber, userstopcode) VALUES (%s, %s, %s, %s);', toinsert)

            if len(removed_userstopcodes) > 0:
                instubs = ', '.join(['%s' for x in range(0, len(removed_userstopcodes))])
                cursor.execute('DELETE FROM kv15_userstopcode WHERE messagecodenumber = %s AND messagecodedate = %s AND dataownercode = %s AND userstopcode IN (' + instubs + ');', [result['messagecodenumber'], result['messagecodedate'], result['dataownercode']] + list(removed_userstopcodes))


            num_lineplanningnumbers = cursor.execute('SELECT kv15_lineplanningnumber.lineplanningnumber FROM kv15_lineplanningnumber WHERE messagecodenumber = %(messagecodenumber)s AND messagecodedate = %(messagecodedate)s AND dataownercode = %(dataownercode)s;', result)
            rows = cursor.fetchall()
            old_lineplanningnumbers = set([row[0] for row in rows])
            
            new_lineplanningnumbers = lineplanningnumbers - old_lineplanningnumbers
            removed_lineplanningnumbers = old_lineplanningnumbers - lineplanningnumbers

            if len(new_lineplanningnumbers) > 0:
                toinsert = [(result['dataownercode'], result['messagecodedate'], result['messagecodenumber'], lineplanningnumber) for lineplanningnumber in new_lineplanningnumbers]
                cursor.executemany('INSERT INTO kv15_lineplanningnumber (dataownercode, messagecodedate, messagecodenumber, lineplanningnumber) VALUES (%s, %s, %s, %s);', toinsert)

            if len(removed_lineplanningnumbers) > 0:
                instubs = ', '.join(['%s' for x in range(0, len(removed_lineplanningnumbers))])
                cursor.execute('DELETE FROM kv15_lineplanningnumber WHERE messagecodenumber = %s AND messagecodedate = %s AND dataownercode = %s AND lineplanningnumber IN (' + instubs + ');', [result['messagecodenumber'], result['messagecodedate'], result['dataownercode']] + list(removed_lineplanningnumbers))

        else:
            columns = ', '.join(result.keys())
            stubs   = ', '.join(['%('+x+')s' for x in result.keys()])
            cursor.execute('INSERT INTO kv15_current ('+ columns +') VALUES (' + stubs + ');', result)
            
            if len(userstopcodes) > 0:
                toinsert = [(result['dataownercode'], result['messagecodedate'], result['messagecodenumber'], userstopcode) for userstopcode in userstopcodes]
                cursor.executemany('INSERT INTO kv15_userstopcode (dataownercode, messagecodedate, messagecodenumber, userstopcode) VALUES (%s, %s, %s, %s);', toinsert)
            if len(lineplanningnumbers) > 0:
                toinsert = [(result['dataownercode'], result['messagecodedate'], result['messagecodenumber'], lineplanningnumber) for lineplanningnumber in lineplanningnumbers]
                cursor.executemany('INSERT INTO kv15_lineplanningnumber (dataownercode, messagecodedate, messagecodenumber, lineplanningnumber) VALUES (%s, %s, %s, %s);', toinsert)
