from gzip import GzipFile
import sys
import codecs

table = None
columns = None

dumping = False

output = codecs.open('/tmp/kv7.sql', 'a', 'UTF-8')

tables = {
    'LOCALSERVICEGROUP': ['DataOwnerCode', 'LocalServiceLevelCode'],
    'LOCALSERVICEGROUPVALIDITY': ['DataOwnerCode', 'LocalServiceLevelCode', 'OperationDate'],
    'LOCALSERVICEGROUPPASSTIME': ['DataOwnerCode', 'LocalServiceLevelCode', 'LinePlanningNumber', 'JourneyNumber', 'FortifyOrderNumber', 'UserStopCode', 'UserStopOrderNumber', 'LineDirection'],
    'TIMINGPOINT': ['DataOwnerCode', 'TimingPointCode'],
    'LINE': ['DataOwnerCode', 'LinePlanningNumber'],
    'DESTINATION': ['DataOwnerCode', 'DestinationCode'],
    'DESTINATIONVIA': ['DataOwnerCode', 'DestinationCodeP', 'DestinationCodeC'],
    'TIMINGPOINT': ['DataOwnerCode', 'TimingPointCode'],
    'USERTIMINGPOINT': ['DataOwnerCode', 'UserStopCode'],
    'DATAOWNER': ['DataOwnerCode'],
    'STOPAREA': ['DataOwnerCode', 'StopAreaCode'],
}

def dumpit():
    global output
    global table
    output.write('\\.\n')

    nonprimary = set(columns) - set(tables[table])
    if nonprimary is None or len(nonprimary) == 0:
        output.write("INSERT INTO %(table)s SELECT * FROM tmp_%(table)s EXCEPT SELECT * FROM %(table)s;\nDELETE FROM tmp_%(table)s;\n" % {'table': table})
    else:
        output.write("WITH upsert_%(table)s AS (UPDATE %(table)s SET %(set)s FROM tmp_%(table)s WHERE %(where)s RETURNING %(table)s.*) INSERT INTO %(table)s SELECT * FROM tmp_%(table)s EXCEPT SELECT * FROM upsert_%(table)s;\nDELETE FROM tmp_%(table)s;\n" % {'table': table, 'set': ', '.join([x + ' = tmp_' + table + '.' + x  for x in nonprimary]), 'where': ' AND '.join([table + '.' + x + ' = tmp_' + table + '.' + x  for x in tables[table]])})


for line in GzipFile(sys.argv[1], 'r'):
    if line[0] == '\\':
        if dumping:
            dumpit()
            dumping = False

        if line[1] == 'L':
            columns = line[2:-2].split('|')
            output.write("COPY tmp_%(table)s (%(columns)s) FROM STDIN CSV DELIMITER '|' NULL AS '';\n" % {'columns': ', '.join(columns), 'table': table})
            dumping = True

        elif line[1] == 'T':
            table = line[2:].split('|')[0]
            
    else:
        line = line.decode('UTF-8')
        output.write(line[:-2].replace('\\0', '') + '\n')

if dumping:
    dumpit()

output.close()
