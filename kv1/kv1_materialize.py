import monetdb.sql
from secret import username, password, sql_username, sql_password, sql_hostname, sql_port, sql_database

from datetime import date
from datetime import datetime
from datetime import time
from datetime import timedelta

weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

sql = """select
pujo.dataownercode, pujo.lineplanningnumber, pujo.journeynumber, pujo.journeypatterncode, timdemrnt.userstopcodebegin, timdemrnt.userstopcodeend, timinglinkorder, pujo.departuretime, totaldrivetime, (usrstopend.userstoptype = 'PASSENGER') as passengerstop
from
pujo, timdemrnt, pegrval, usrstop as usrstopbegin, usrstop as usrstopend
where
pujo.dataownercode = timdemrnt.dataownercode and
pujo.lineplanningnumber = timdemrnt.lineplanningnumber and
pujo.journeypatterncode = timdemrnt.journeypatterncode and
pujo.timedemandgroupcode = timdemrnt.timedemandgroupcode and
pujo.dataownercode = pegrval.dataownercode and
pujo.timetableversioncode = pegrval.periodgroupcode and
timdemrnt.dataownercode = usrstopbegin.dataownercode and
timdemrnt.dataownercode = usrstopend.dataownercode and
timdemrnt.userstopcodebegin = usrstopbegin.userstopcode and
timdemrnt.userstopcodeend = usrstopend.userstopcode and
pujo.daytype%(weekday)s = True and
'%(operatingday)s' between pegrval.validfrom and pegrval.validthru
order by
pujo.dataownercode, pujo.lineplanningnumber, pujo.departuretime,  pujo.timetableversioncode, pujo.journeypatterncode, pujo.timedemandgroupcode, timdemrnt.timinglinkorder
;"""

connection = monetdb.sql.connect(username=sql_username, password=sql_password, hostname=sql_hostname, port=sql_port, database=sql_database, autocommit=False)
cursor = connection.cursor()

today = date().today()
weekday = weekdays[today.weekday()]

tmp_passagesequence = {}
tmp_passtime = None
tmp_orderguard = 1000

print sql % {'operatingday': str(today), 'weekday': weekday}
exit;

cursor.execute(sql % {'operatingday': str(today), 'weekday': weekday})
for row in cursor.fetchall():
    dataownercode, lineplanningnumber, journeynumber, journeypatterncode, userstopcodebegin, userstopcodeend, timinglinkorder, departuretime, totaldrivetime, passengerstop = row
    if timinglinkorder == 0 or (timinglinkorder == 1 and len(tmp_passagesequence) > 1):
        if len(tmp_passagesequence) > 0:
            connection.commit()
            tmp_passagesequence = {}

        tmp_passagesequence[userstopcodebegin] = 0
        tmp_passtime = datetime(year=today.year, month=today.month, day=(today.day + (departuretime.day-1)), hour=departuretime.hour, minute=departuretime.minute, second=departuretime.second)
        cursor.execute("INSERT INTO kv1_current VALUES (%s, %s, %s, %s, %s, %s, %s, %s);", [dataownercode, lineplanningnumber, str(today), journeynumber, journeypatterncode, userstopcodebegin, tmp_passagesequence[userstopcodebegin], tmp_passtime]);

    elif tmp_orderguard > timinglinkorder:
        print dataownercode, lineplanningnumber, journeynumber, userstopcodebegin, timinglinkorder
    
    if userstopcodeend in tmp_passagesequence:
        tmp_passagesequence[userstopcodeend] += 1
    else:
        tmp_passagesequence[userstopcodeend] = 0

    tmp_passtime += timedelta(seconds=int(totaldrivetime))

    cursor.execute("INSERT INTO kv1_current VALUES (%s, %s, %s, %s, %s, %s, %s, %s);", [dataownercode, lineplanningnumber, str(today), journeynumber, journeypatterncode, userstopcodeend, tmp_passagesequence[userstopcodeend], tmp_passtime]);
    tmp_orderguard = timinglinkorder
 
connection.commit()
