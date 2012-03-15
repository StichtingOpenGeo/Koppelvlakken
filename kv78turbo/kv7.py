from ctx import ctx
import codecs
import os
import sys
import simplejson

def KV7kalender(contents):
    c = ctx(contents)
    if 'LOCALSERVICEGROUP' in c.ctx:
        localservicegroup = [row['DataOwnerCode'] + '_' + row['LocalServiceLevelCode'] for row in c.ctx['LOCALSERVICEGROUP'].rows()]

        if 'LOCALSERVICEGROUPVALIDITY' in c.ctx:
            localservicegroupvalidity = {}
            for row in c.ctx['LOCALSERVICEGROUPVALIDITY'].rows():
                localservicelevelcode = row['DataOwnerCode'] + '_' + row['LocalServiceLevelCode']
                if localservicelevelcode in localservicegroup:
                    if row['OperationDate'] not in localservicegroupvalidity:
                        localservicegroupvalidity[row['OperationDate']] = [localservicelevelcode]
                    else:
                        localservicegroupvalidity[row['OperationDate']].append(localservicelevelcode)

            return localservicegroupvalidity

def KV7planning(contents):
    result = {}
    c = ctx(contents)
    if 'DATAOWNER' in c.ctx:
        result['DATAOWNER'] = c.ctx['DATAOWNER'].rowsdict(['DataOwnerCode'])

    if 'DESTINATION' in c.ctx:
        result['DESTINATION'] = c.ctx['DESTINATION'].rowsdict(['DataOwnerCode', 'DestinationCode'])

    if 'USERTIMINGPOINT' in c.ctx:
        result['USERTIMINGPOINT'] = c.ctx['USERTIMINGPOINT'].rowsdict(['DataOwnerCode', 'UserStopCode'])
    
    if 'LINE' in c.ctx:
        result['LINE'] = c.ctx['LINE'].rowsdict(['DataOwnerCode', 'LinePlanningNumber'])

    if 'LOCALSERVICEGROUPPASSTIME' in c.ctx:
        result['LOCALSERVICEGROUPPASSTIME'] = {}
        for row in c.ctx['LOCALSERVICEGROUPPASSTIME'].rows():
            localservicegrouppasstime = row['DataOwnerCode'] + '_' + row['LocalServiceLevelCode']
            lineplanningnumber = '_'.join([row['DataOwnerCode'], row['LinePlanningNumber'], row['LineDirection']])
            journeynumber = '_'.join([row['DataOwnerCode'], row['LocalServiceLevelCode'], row['LinePlanningNumber'], row['JourneyNumber'], row['FortifyOrderNumber']])

            if localservicegrouppasstime not in result['LOCALSERVICEGROUPPASSTIME']:
                result['LOCALSERVICEGROUPPASSTIME'][localservicegrouppasstime] = { lineplanningnumber: { journeynumber: { int(row['UserStopOrderNumber']): row } } }
            elif lineplanningnumber not in result['LOCALSERVICEGROUPPASSTIME'][localservicegrouppasstime]:
                result['LOCALSERVICEGROUPPASSTIME'][localservicegrouppasstime][lineplanningnumber] = { journeynumber: { int(row['UserStopOrderNumber']): row } }
            elif journeynumber not in result['LOCALSERVICEGROUPPASSTIME'][localservicegrouppasstime][lineplanningnumber]:
                result['LOCALSERVICEGROUPPASSTIME'][localservicegrouppasstime][lineplanningnumber][journeynumber] = { int(row['UserStopOrderNumber']): row }
            else:
                result['LOCALSERVICEGROUPPASSTIME'][localservicegrouppasstime][lineplanningnumber][journeynumber][int(row['UserStopOrderNumber'])] = row
                
    if 'TIMINGPOINT' in c.ctx:
        result['TIMINGPOINT'] = c.ctx['TIMINGPOINT'].rowsdict(['TimingPointCode'])

    return result

def KV7planning_merge(result1, result2):
    for key in result1.keys():
        result1[key].update(result2[key])

    for key in (set(result2.keys()) - set(result1.keys())):
        result1[key] = result2[key]

    return result1

results = {}

for filename in os.listdir(sys.argv[2]):
    contents = codecs.open(sys.argv[2] + '/' + filename, 'r', 'UTF-8').read()
    results = KV7planning_merge(results, KV7planning(contents))

contents = codecs.open(sys.argv[1], 'r', 'UTF-8').read()
results['LOCALSERVICEGROUPVALIDITY'] = KV7kalender(contents)

f = open('/tmp/kv7.json', 'w')
f.write(simplejson.dumps(results, sort_keys=True, indent=4))
f.close()

print results['LOCALSERVICEGROUPPASSTIME'].keys()

print results['LOCALSERVICEGROUPPASSTIME']['GVB_28144']['GVB_902_2']['GVB_28144_902_284_0'][1]
