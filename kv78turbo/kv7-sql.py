from ctx import ctx
import codecs
import os
import sys
import simplejson

header = """
CREATE TABLE "sys"."dataowner" (
        "dataownercode"          VARCHAR(10)   NOT NULL,
        "dataownertype"          VARCHAR(10)   NOT NULL,
        "dataownername"          VARCHAR(30)   NOT NULL,
        "dataownercompanynumber" DECIMAL(3),
        CONSTRAINT "dataowner_dataownercode_pkey" PRIMARY KEY ("dataownercode")
);
CREATE TABLE "sys"."line" (
        "dataownercode"      VARCHAR(10)   NOT NULL,
        "lineplanningnumber" VARCHAR(10)   NOT NULL,
        "linepublicnumber"   VARCHAR(4)    NOT NULL,
        "linename"           VARCHAR(50),
        "linevetagnumber"    DECIMAL(3),
        "transporttype"      VARCHAR(5)    NOT NULL,
        CONSTRAINT "line_dataownercode_lineplanningnumber_pkey" PRIMARY KEY ("dataownercode", "lineplanningnumber")
);
CREATE TABLE "sys"."destination" (
        "dataownercode"        VARCHAR(10)   NOT NULL,
        "destinationcode"      VARCHAR(10)   NOT NULL,
        "destinationname50"    VARCHAR(50)   NOT NULL,
        "destinationname30"    VARCHAR(30),
        "destinationname24"    VARCHAR(24),
        "destinationname19"    VARCHAR(19),
        "destinationname16"    VARCHAR(16)   NOT NULL,
        "destinationdetail24"  VARCHAR(24),
        "destinationdetail19"  VARCHAR(19),
        "destinationdetail16"  VARCHAR(16),
        "destinationdisplay16" VARCHAR(16),
        CONSTRAINT "destination_dataownercode_destinationcode_pkey" PRIMARY KEY ("dataownercode", "destinationcode")
);
CREATE TABLE "sys"."destinationvia" (
        "dataownercode"         VARCHAR(10)   NOT NULL,
        "destinationcodep"      VARCHAR(10)   NOT NULL,
        "destinationcodec"      VARCHAR(10)   NOT NULL,
        "destinationviaordernr" TINYINT       NOT NULL,
        CONSTRAINT "destinationvia_dataownercode_destinationcodep_destinationcodec_pkey" PRIMARY KEY ("dataownercode", "destinationcodep", "destinationcodec")
);
CREATE TABLE "sys"."timingpoint" (
        "dataownercode"   VARCHAR(10)   NOT NULL,
        "timingpointcode" VARCHAR(10)   NOT NULL,
        "timingpointname" VARCHAR(50)   NOT NULL,
        "timingpointtown" VARCHAR(50)   NOT NULL,
        "stopareacode"    VARCHAR(10),
        CONSTRAINT "timingpoint_dataownercode_timingpointcode_pkey" PRIMARY KEY ("dataownercode", "timingpointcode")
);
CREATE TABLE "sys"."usertimingpoint" (
        "dataownercode"            VARCHAR(10)   NOT NULL,
        "userstopcode"             VARCHAR(10)   NOT NULL,
        "timingpointdataownercode" VARCHAR(10)   NOT NULL,
        "timingpointcode"          VARCHAR(10)   NOT NULL,
        CONSTRAINT "usertimingpoint_dataownercode_userstopcode_pkey" PRIMARY KEY ("dataownercode", "userstopcode")
);
CREATE TABLE "sys"."localservicegrouppasstime" (
        "dataownercode"         VARCHAR(10)   NOT NULL,
        "localservicelevelcode" VARCHAR(10)   NOT NULL,
        "lineplanningnumber"    VARCHAR(10)   NOT NULL,
        "journeynumber"         DECIMAL(6)    NOT NULL,
        "fortifynumber"         DECIMAL(2)    NOT NULL,
        "userstopcode"          VARCHAR(10)   NOT NULL,
        "userstopordernumber"   DECIMAL(3)    NOT NULL,
        "linedirection"         DECIMAL       NOT NULL,
        "destinationcode"       VARCHAR(10)   NOT NULL,
        "targetarrivaltime"     VARCHAR(8)    NOT NULL,
        "targetdeparturetime"   VARCHAR(8)    NOT NULL,
        "sidecode"              VARCHAR(10)   NOT NULL,
        "wheelchairaccesible"   BOOLEAN,
        "journeystoptype"       VARCHAR(12)   NOT NULL,
        "istimingstop"          BOOLEAN       NOT NULL,
        "productformulatype"    DECIMAL(4),
        CONSTRAINT "localservicegrouppasstime_dataownercode_localservicelevelcode_lineplanningnumber_journeynumber_fortifynumber_userstopcode_userstopordernumber_pkey" PRIMARY KEY ("dataownercode", "localservicelevelcode", "lineplanningnumber", "journeynumber", "fortifynumber", "userstopcode", "userstopordernumber")
);
CREATE TABLE "sys"."localservicegroup" (
        "dataownercode"         VARCHAR(10)   NOT NULL,
        "localservicelevelcode" VARCHAR(10)   NOT NULL,
        CONSTRAINT "localservicegroup_dataownercode_localservicelevelcode_pkey" PRIMARY KEY ("dataownercode", "localservicelevelcode")
);
CREATE TABLE "sys"."localservicegroupvalidity" (
        "dataownercode"         VARCHAR(10)   NOT NULL,
        "localservicelevelcode" VARCHAR(10)   NOT NULL,
        "operationdate"         DATE          NOT NULL,
        CONSTRAINT "localservicegroupvalidity_dataownercode_localservicelevelcode_operationdate_pkey" PRIMARY KEY ("dataownercode", "localservicelevelcode", "operationdate")
);
GRANT SELECT ON dataowner TO dbslayer;
GRANT SELECT ON line TO dbslayer;
GRANT SELECT ON destination TO dbslayer;
GRANT SELECT ON destinationvia TO dbslayer;
GRANT SELECT ON timingpoint TO dbslayer;
GRANT SELECT ON usertimingpoint TO dbslayer;
GRANT SELECT ON localservicegrouppasstime TO dbslayer;
GRANT SELECT ON localservicegroup TO dbslayer;
GRANT SELECT ON localservicegroupvalidity TO dbslayer;

"""
tmp_tables = """
CREATE TABLE "tmp_dataowner" (
        "dataownercode"          VARCHAR(10)   NOT NULL,
        "dataownertype"          VARCHAR(10)   NOT NULL,
        "dataownername"          VARCHAR(30)   NOT NULL,
        "dataownercompanynumber" DECIMAL(3)
);
CREATE TABLE "tmp_line" (
        "dataownercode"      VARCHAR(10)   NOT NULL,
        "lineplanningnumber" VARCHAR(10)   NOT NULL,
        "linepublicnumber"   VARCHAR(4)    NOT NULL,
        "linename"           VARCHAR(50),
        "linevetagnumber"    DECIMAL(3),
        "transporttype"      VARCHAR(5)    NOT NULL
);
CREATE TABLE "tmp_destination" (
        "dataownercode"        VARCHAR(10)   NOT NULL,
        "destinationcode"      VARCHAR(10)   NOT NULL,
        "destinationname50"    VARCHAR(50)   NOT NULL,
        "destinationname30"    VARCHAR(30),
        "destinationname24"    VARCHAR(24),
        "destinationname19"    VARCHAR(19),
        "destinationname16"    VARCHAR(16)   NOT NULL,
        "destinationdetail24"  VARCHAR(24),
        "destinationdetail19"  VARCHAR(19),
        "destinationdetail16"  VARCHAR(16),
        "destinationdisplay16" VARCHAR(16)
);
CREATE TABLE "tmp_destinationvia" (
        "dataownercode"         VARCHAR(10)   NOT NULL,
        "destinationcodep"      VARCHAR(10)   NOT NULL,
        "destinationcodec"      VARCHAR(10)   NOT NULL,
        "destinationviaordernr" TINYINT       NOT NULL
);
CREATE TABLE "tmp_timingpoint" (
        "dataownercode"   VARCHAR(10)   NOT NULL,
        "timingpointcode" VARCHAR(10)   NOT NULL,
        "timingpointname" VARCHAR(50)   NOT NULL,
        "timingpointtown" VARCHAR(50)   NOT NULL,
        "stopareacode"    VARCHAR(10)
);
CREATE TABLE "tmp_usertimingpoint" (
        "dataownercode"            VARCHAR(10)   NOT NULL,
        "userstopcode"             VARCHAR(10)   NOT NULL,
        "timingpointdataownercode" VARCHAR(10)   NOT NULL,
        "timingpointcode"          VARCHAR(10)   NOT NULL
);
CREATE TABLE "tmp_localservicegrouppasstime" (
        "dataownercode"         VARCHAR(10)   NOT NULL,
        "localservicelevelcode" VARCHAR(10)   NOT NULL,
        "lineplanningnumber"    VARCHAR(10)   NOT NULL,
        "journeynumber"         DECIMAL(6)    NOT NULL,
        "fortifynumber"         DECIMAL(2)    NOT NULL,
        "userstopcode"          VARCHAR(10)   NOT NULL,
        "userstopordernumber"   DECIMAL(3)    NOT NULL,
        "linedirection"         DECIMAL       NOT NULL,
        "destinationcode"       VARCHAR(10)   NOT NULL,
        "targetarrivaltime"     VARCHAR(8)    NOT NULL,
        "targetdeparturetime"   VARCHAR(8)    NOT NULL,
        "sidecode"              VARCHAR(10)   NOT NULL,
        "wheelchairaccesible"   BOOLEAN,
        "journeystoptype"       VARCHAR(12)   NOT NULL,
        "istimingstop"          BOOLEAN       NOT NULL,
        "productformulatype"    DECIMAL(4)
);
CREATE TABLE "tmp_localservicegroup" (
        "dataownercode"         VARCHAR(10)   NOT NULL,
        "localservicelevelcode" VARCHAR(10)   NOT NULL
);
CREATE TABLE "tmp_localservicegroupvalidity" (
        "dataownercode"         VARCHAR(10)   NOT NULL,
        "localservicelevelcode" VARCHAR(10)   NOT NULL,
        "operationdate"         DATE          NOT NULL
);

"""

def copy_table(c, table, keys):
    if table in c.ctx:
        rows = c.ctx[table].columns()
        table = table.lower()
        print """COPY %d RECORDS INTO tmp_%s FROM stdin USING DELIMITERS '\\t','\\n' NULL AS '';""" % (len(rows[keys[0]]), table)
        for x in range(0, len(rows[keys[0]])):
            print '\t'.join([str(rows[k][x] or '') for k in keys])

        print """INSERT INTO "sys".%s SELECT * FROM tmp_%s EXCEPT SELECT * FROM "sys".%s;""" % (table, table, table)
        print """DELETE FROM tmp_%s;""" % (table)
 
def KV7kalender(contents):
    c = ctx(contents)
    copy_table(c, 'LOCALSERVICEGROUP', ['DataOwnerCode', 'LocalServiceLevelCode'])
    copy_table(c, 'LOCALSERVICEGROUPVALIDITY', ['DataOwnerCode', 'LocalServiceLevelCode', 'OperationDate'])

def KV7planning(contents):
    result = {}
    c = ctx(contents)
    copy_table(c, 'LINE', ['DataOwnerCode', 'LinePlanningNumber', 'LinePublicNumber', 'LineName', 'LineVeTagNumber', 'TransportType'])
    copy_table(c, 'DESTINATION', ['DataOwnerCode', 'DestinationCode', 'DestinationName50', 'DestinationName30','DestinationName24','DestinationName19','DestinationName16','DestinationDetail24', 'DestinationDetail19', 'DestinationDetail16', 'DestinationDisplay16'])
    copy_table(c, 'DESTINATIONVIA', ['DataOwnerCode', 'DestinationCodeP', 'DestinationCodeC', 'DestinationViaOrderNr'])
    copy_table(c, 'TIMINGPOINT', ['DataOwnerCode', 'TimingPointCode', 'TimingPointName', 'TimingPointTown', 'StopAreaCode'])
    copy_table(c, 'USERTIMINGPOINT', ['DataOwnerCode', 'UserStopCode', 'TimingPointDataOwnerCode', 'TimingPointCode'])

    if 'LOCALSERVICEGROUPPASSTIME' in c.ctx:
        rows = c.ctx['LOCALSERVICEGROUPPASSTIME'].columns()
        print """COPY %d RECORDS INTO "sys".LOCALSERVICEGROUPPASSTIME FROM stdin USING DELIMITERS '\\t','\\n' NULL AS '';""" % (len(rows['DataOwnerCode']))
        for x in range(0, len(rows['DataOwnerCode'])):
            if rows['WheelChairAccessible'][x] == 'ACCESSIBLE':
                WheelChairAccessible = True
            elif rows['WheelChairAccessible'][x] == 'NOTACCESSIBLE':
                WheelChairAccessible = False
            else:
                WheelChairAccessible = None

            IsTimingStop = (rows['IsTimingStop'][x] == '1')

            print '\t'.join([rows['DataOwnerCode'][x], rows['LocalServiceLevelCode'][x], rows['LinePlanningNumber'][x],
                             rows['JourneyNumber'][x], rows['FortifyOrderNumber'][x], rows['UserStopCode'][x], rows['UserStopOrderNumber'][x],
                             rows['LineDirection'][x], rows['DestinationCode'][x], rows['TargetArrivalTime'][x], rows['TargetDepartureTime'][x],
                             rows['SideCode'][x], str(WheelChairAccessible or '').lower(), rows['JourneyStopType'][x], str(IsTimingStop).lower(),
                             rows['ProductFormulaType'][x]])


clear = True
if clear:
    print """
DROP TABLE dataowner;
DROP TABLE line;
DROP TABLE destination;
DROP TABLE destinationvia;
DROP TABLE timingpoint;
DROP TABLE usertimingpoint;
DROP TABLE localservicegrouppasstime;
DROP TABLE localservicegroup;
DROP TABLE localservicegroupvalidity;
DROP TABLE tmp_dataowner;
DROP TABLE tmp_line;
DROP TABLE tmp_destination;
DROP TABLE tmp_destinationvia;
DROP TABLE tmp_timingpoint;
DROP TABLE tmp_usertimingpoint;
DROP TABLE tmp_localservicegrouppasstime;
DROP TABLE tmp_localservicegroup;
DROP TABLE tmp_localservicegroupvalidity;
"""
    print header

print "START TRANSACTION;"
print tmp_tables


for filename in os.listdir(sys.argv[2]):
    contents = codecs.open(sys.argv[2] + '/' + filename, 'r', 'UTF-8').read()
    KV7planning(contents)

contents = codecs.open(sys.argv[1], 'r', 'UTF-8').read()
KV7kalender(contents)

print "COMMIT;"
