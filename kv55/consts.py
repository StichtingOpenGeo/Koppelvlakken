KV55_RES = """<?xml version="1.0"?><DRIS_55_RES><SubscriberID>openOV</SubscriberID><Version>0.0.2</Version><DossierName>KV55</DossierName><SendTimestamp>%(timestamp)s</SendTimestamp><ResponseCode>OK</ResponseCode></DRIS_55_RES>"""
KV55_REQ = """<?xml version="1.0"?><DRIS_55_REQ><SubscriberID>openOV</SubscriberID><Version>0.0.2</Version><DossierName>KV55</DossierName><SendTimestamp>%(timestamp)s</SendTimestamp><Request><RequestTimestamp>%(timestamp)s</RequestTimestamp><SequenceNumber>%(sequencenumber)d</SequenceNumber><TimingPoint><TimingPointCode>%(timingpointcode)s</TimingPointCode></TimingPoint></Request></DRIS_55_REQ>"""
KV55_REP = """<?xml version="1.0"?><DRIS_55><SubscriberID>openOV</SubscriberID><Version>0.0.2</Version><DossierName>KV55</DossierName><Request><TimingPoint><TimingPointCode>%(timingpointcode)s</TimingPointCode></TimingPoint><Error>%(error)s</Error></Request></DRIS_55>"""

GOVI_KV55_URL = 'http://drisacc.transmodel.nl/TMI_Post/KV55/openOV'

ZMQ_SERVER = "tcp://127.0.0.1:6055"
ZMQ_PUBSUB = "tcp://127.0.0.1:6056"

REQUEST_TIMEOUT = 2000
