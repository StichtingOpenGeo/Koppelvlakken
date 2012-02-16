KV7_RES = """<?xml version="1.0"?><tmi8:DRIS_TM_RES xmlns:tmi8="http://bison.connekt.nl/tmi8/kv7/msg" />"""
KV55_RES = """<?xml version="1.0"?><DRIS_55_RES><SubscriberID>openOV</SubscriberID><Version>0.0.1</Version><DossierName>KV55</DossierName><SendTimestamp>%(timestamp)s</SendTimestamp><ResponseCode>OK</ResponseCode></DRIS_55_RES>"""
KV55_REQ = """<?xml version="1.0"?><DRIS_55_REQ><SubscriberID>openOV</SubscriberID><Version>0.0.1</Version><DossierName>KV55</DossierName><SendTimestamp>%(timestamp)s</SendTimestamp><Request><RequestTimestamp>%(timestamp)s</RequestTimestamp><SequenceNumber>%(sequencenumber)d</SequenceNumber><TimingPoint><TimingPointCode>%(timingpointcode)s</TimingPointCode></TimingPoint></Request></DRIS_55_REQ>"""
KV55_ERROR = """<?xml version="1.0"?><DRIS_55><SubscriberID>openOV</SubscriberID><Version>0.0.1</Version><DossierName>KV55</DossierName><Request><TimingPoint><TimingPointCode>%(timingpointcode)s</TimingPointCode></TimingPoint><Error>%(error)s</Error></Request></DRIS_55>"""
KV55_REP = """<?xml version="1.0"?><DRIS_55><SubscriberID>OpenOV</SubscriberID><Version>0.0.1</Version><DossierName>KV55</DossierName><SendTimestamp>%(sent)s</SendTimestamp><License>http://creativecommons.org/publicdomain/zero/1.0/</License><Request><RequestTimestamp>%(request)s</RequestTimestamp><SequenceNumber>%(sequencenumber)d</SequenceNumber><TimingPoint><TimingPointCode>%(tpc)s</TimingPointCode>%(trips)s</TimingPoint></Request></DRIS_55>"""
KV55_TRIP = """<Trip><OperatingDate>%(operdate)s</OperatingDate><DataOwnerCode>ARR</DataOwnerCode><LinePlanningNumber>%(linenumber)s</LinePlanningNumber><LinePublicNumber>%(linenumber)s</LinePublicNumber><DestinationName>(%(linenumber)s) %(linename)s</DestinationName><JourneyNumber>%(journeynumber)d</JourneyNumber><FortifyOrderNumber>%(fortifyordernumber)d</FortifyOrderNumber><TargetDepartureTime>%(target)s</TargetDepartureTime><ExpectedDepartureTime>%(expected)s</ExpectedDepartureTime><TripStopStatus>%(tripstopstatus)s</TripStopStatus></Trip>"""

GOVI_KV55_URL = 'http://drisacc.transmodel.nl/TMI_Post/KV55/openOV'
ARRIVA_REALTIME_URL = "http://www.arriva.nl/nc/reisinformatie/vertrektijden-zoeken/actuele-vertrektijden/detailpagina/?tx_bwrealtime_pi1[stop]=%s"

ZMQ_SERVER = "tcp://127.0.0.1:6055"
ZMQ_PUBSUB_GOVI   = "tcp://127.0.0.1:6056"
ZMQ_PUBSUB_ARRIVA = "tcp://127.0.0.1:6057"
ZMQ_ARRIVA = "tcp://127.0.0.1:6058"

REQUEST_TIMEOUT = 45000
CLEANUP_TIMEOUT = 60000
