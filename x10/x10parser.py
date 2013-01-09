import sys
import os
import re

def vdv_reader(filename):
    f = open(filename)
    chs = ''
    state = 'h'
    tbl = ''
    e_atr = []
    e_frm = []
    create = ''
    recs = []

    while True:
        line = f.readline()
        if len(line) == 0:
            break

        line = line.replace('\r\n', '')

        if line == '':
            tbl = ''
            e_atr = []
            e_frm = []
            create = ''
            recs = []
            continue

        if state == 'h':
            if line.startswith('chs'):
                chs = line.split('; ')[1].replace('"', '').replace('ISO', 'ISO-')
            if line.startswith('tbl'):
                state = 'b'

        if state == 'b':
            if line.startswith('tbl'):
                tbl = line.split('; ')[1].replace('"', '')
            elif line.startswith('atr'):
                e_atr = line.split(';')[1:]
            elif line.startswith('frm'):
                x  = re.compile('(num\[\d.\d\])')
                line = x.sub('bigint', line) # In holland is a company, that is is doing very well, can't configure IIS, accepts lousy data, doesn't enforce. This is hack to counter that
                e_frm = line.replace('num', 'numeric').replace('char', 'varchar').replace('.', ',').replace('[','(').replace(']',')').replace('varchar(6)','varchar(10)').split(';')[1:] #Contains hack to counter varchar(6) stupid closed-data
            elif line.startswith('rec'):
                recs.append(line.replace('rec; ', '').replace('; ', '\t').replace('"', '').replace('null','').replace('NULL', ''))
            elif line.startswith('end') and len(recs) > 0:
                print 'create table ' + tbl + ' (' + ', '.join([e_atr[x] + ' ' + e_frm[x] for x in range(0, len(e_frm))]) + ');'
                print 'copy ' + tbl + '(' + ','.join(e_atr) + ') FROM stdin NULL AS \'\' ENCODING \''+chs+'\';';
                print '\n'.join(recs)
                print '\.'

for x in os.listdir(sys.argv[1]):
    vdv_reader(sys.argv[1]+'/'+x)
    #if x.endswith('.x10'):
    #    vdv_reader(sys.argv[1]+'/'+x)
