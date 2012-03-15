from ctx import ctx
import codecs
import sys

def KV7kalender(contents):
    c = ctx(contents)
    if 'LOCALSERVICEGROUP' in c.ctx:
        localservicegroup = set([row['DataOwnerCode'] + '_' + row['LocalServiceLevelCode'] for row in c.ctx['LOCALSERVICEGROUP'].rows()])

        if 'LOCALSERVICEGROUPVALIDITY' in c.ctx:
            localservicegroupvalidity = {}
            for row in c.ctx['LOCALSERVICEGROUPVALIDITY'].rows():
                localservicelevelcode = row['DataOwnerCode'] + '_' + row['LocalServiceLevelCode']
                if localservicelevelcode in localservicegroup:
                    if row['OperationDate'] not in localservicegroupvalidity:
                        localservicegroupvalidity[row['OperationDate']] = set([localservicelevelcode])
                    else:
                        localservicegroupvalidity[row['OperationDate']].add(localservicelevelcode)

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


contents = codecs.open(sys.argv[1], 'r', 'UTF-8').read()
localservicegroupvalidity = KV7kalender(contents)

contents = codecs.open(sys.argv[2], 'r', 'UTF-8').read()
result = KV7planning(contents)

#print localservicegroupvalidity
#print len(result['LOCALSERVICEGROUPPASSTIME'][localservicegroupvalidity['2012-03-15'].pop()])
#key = 'GVB_28144'
#print result['LOCALSERVICEGROUPPASSTIME'][key]['GVB_902_2']['GVB_28144_902_284_0'][1]
