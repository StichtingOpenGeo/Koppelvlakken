from ctx import ctx
import codecs
import sys

def KV7kalender(contents):
    c = ctx(contents)
    if 'LOCALSERVICEGROUP' in c.ctx:
        localservicegroup = set([row['DataOwnerCode'] + '_' + row['LocalServiceLevelCode'] for row in c.ctx['LOCALSERVICEGROUP'].rows()])
        localservicegroupvalidity = {}
        for row in c.ctx['LOCALSERVICEGROUPVALIDITY'].rows():
            localservicelevelcode = row['DataOwnerCode'] + '_' + row['LocalServiceLevelCode']
            if localservicelevelcode in localservicegroup:
                if row['OperationDate'] not in localservicegroupvalidity:
                    localservicegroupvalidity[row['OperationDate']] = set([localservicelevelcode])
                else:
                    localservicegroupvalidity[row['OperationDate']].add(localservicelevelcode)

        return localservicegroupvalidity

contents = codecs.open(sys.argv[1], 'r', 'UTF-8').read()
print KV7kalender(contents)

