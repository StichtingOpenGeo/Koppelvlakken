import codecs
import sys
from datetime import date, timedelta
import time

charset = 'cp1252' # yes, this isn't what the documentation suggests
path = sys.argv[1] + '/'

#parse stops
f = codecs.open('/tmp/stops.tsv', 'w', 'UTF-8')
l_content = codecs.open(path + 'RET.HLT', 'r', charset).read().split('\r\n')
for stop in l_content[:-1]:
    properties = stop.split(',')
    for i in range(len(properties)):
        properties[i] = properties[i].strip()
    f.write('|'.join(properties) + '\n')

def parse_date(day):
	return date(int(day[4:8]), int(day[2:4]), int(day[0:2]))

def parse_time(time):
	return time[0:2] + ':' + time[2:4] + ':00'

def add24u(time):
    hours = str(int(time[0:2])+24)
    return hours+time[2:]

def antitijdreis(rit):
    for i in range(1, len(rit)):
       if rit[i][7] < rit[i-1][7]:
           rit[i][7] = add24u(rit[i][7])
    for i in range(0, len(rit)-1):
       if rit[i][8] < rit[i-1][8]:
           rit[i][8] = add24u(rit[i][8])
    return rit

#read pas file
# pujo: transportmode,modaliteit,vervoerdercode,lijnsysteemnr,richting,ritnummer,voetnoot
l_content = codecs.open(path + 'RET.PAS', 'r', charset).read().split('\r\n')
pujofile = codecs.open('/tmp/pujo.tsv', 'w', 'UTF-8')
pujofile.write('modaliteit|vervoerdercode|lijnsysteemnr|richting|ritnummer|voetnoot\n')
stopsfile = codecs.open('/tmp/pujopass.tsv', 'w', 'UTF-8')
stopsfile.write('vervoerdercode|lijnsysteemnr|richting|ritnummer|stopsequentie|halteid|aankomsttijd|vertrektijd')
counter = 0
rit = []
for line in l_content[:-1]:
    if line[0] == '!':
        assert(line[1:] == 'RETPAS1')
    elif line[0] == '&':
        geldigvan,geldigtot = line[1:].split('-')
    elif line[0] == '#':
        counter = 0
        pujo = line[1:].split(',')
        rit = []
    elif line[0] == '-':
        pujo.append(line[1:])
        pujofile.write('|'.join(pujo)+'\n')
    elif line[0] == '>':
        counter += 1
        halteid,vertrektijd = line[1:].split(',')
        rit.append([pujo[1],pujo[2],pujo[3],pujo[4],pujo[5],str(counter),halteid.strip(),'',parse_time(vertrektijd)])
    elif line[0] == '.':
        counter += 1
        halteid,aankomstvertrektijd = line[1:].split(',')
        rit.append([pujo[1],pujo[2],pujo[3],pujo[4],pujo[5],str(counter),halteid.strip(),parse_time(aankomstvertrektijd),parse_time(aankomstvertrektijd)])
    elif line[0] == '+':
        counter += 1
        halteid,aankomsttijd,vertrektijd = line[1:].split(',')
        rit.append([pujo[1],pujo[2],pujo[3],pujo[4],pujo[5],str(counter),halteid.strip(),parse_time(aankomsttijd),parse_time(vertrektijd)])
    elif line[0] == '<':
        counter += 1
        halteid,aankomsttijd = line[1:].split(',')
        rit.append([pujo[1],pujo[2],pujo[3],pujo[4],pujo[5],str(counter),halteid.strip(),parse_time(aankomsttijd),''])
        antitijdreis(rit)
        for stop in rit:
            stopsfile.write('|'.join(stop)+'\n')

footnotes = {}
current_id = None
voetnootfile = codecs.open('/tmp/voetnoot.tsv', 'w', 'UTF-8')
voetnootfile.write('voetnoot|datum\n')
l_content = codecs.open(path + 'RET.VTN', 'r', charset).read().split('\r\n')
eerstedag = parse_date(geldigvan)
for line in l_content[:-1]:
    if line[0] == '@':
        footnote,validity = line[1:].split(',')
        for z in range(0, len(validity)):
            voetnootfile.write(footnote+'|'+(eerstedag + timedelta(days=z)).strftime("%Y-%m-%d")+'\n')
