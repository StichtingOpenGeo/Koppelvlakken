ISO_TIME = "%Y-%m-%dT%H:%M:%S+0200"

KV17_SUBSCRIBERID = "openOV"
KV17_VERSION = "BISON 8.1.0.0"
KV17_DOSSIERNAME = "KV17cvlinfo"

KV17_PSHOST = "kv17.xmpp.openov.nl"

KV17_OK = """<?xml version="1.0" encoding="UTF-8"?><tmi8:VV_TM_RES xmlns:tmi8="http://bison.connekt.nl/tmi8/kv17/msg"><tmi8:SubscriberID>"""+KV17_SUBSCRIBERID+"""</tmi8:SubscriberID><tmi8:Version>"""+KV17_VERSION+"""</tmi8:Version><tmi8:DossierName>"""+KV17_DOSSIERNAME+"""</tmi8:DossierName><tmi8:Timestamp>%s</tmi8:Timestamp><tmi8:ResponseCode>OK</tmi8:ResponseCode></tmi8:VV_TM_RES>"""

KV17_SE = """<?xml version="1.0" encoding="UTF-8"?><tmi8:VV_TM_RES xmlns:tmi8="http://bison.connekt.nl/tmi8/kv17/msg"><tmi8:SubscriberID>"""+KV17_SUBSCRIBERID+"""</tmi8:SubscriberID><tmi8:Version>"""+KV17_VERSION+"""</tmi8:Version><tmi8:DossierName>"""+KV17_DOSSIERNAME+"""</tmi8:DossierName><tmi8:Timestamp>%s</tmi8:Timestamp><tmi8:ResponseCode>SE</tmi8:ResponseCode><tmi8:ResponseError><![CDATA[%s]]></tmi8:ResponseError></tmi8:VV_TM_RES>"""

KV17_NOK = """<?xml version="1.0" encoding="UTF-8"?><tmi8:VV_TM_RES xmlns:tmi8="http://bison.connekt.nl/tmi8/kv17/msg"><tmi8:SubscriberID>"""+KV17_SUBSCRIBERID+"""</tmi8:SubscriberID><tmi8:Version>"""+KV17_VERSION+"""</tmi8:Version><tmi8:DossierName>"""+KV17_DOSSIERNAME+"""</tmi8:DossierName><tmi8:Timestamp>%s</tmi8:Timestamp><tmi8:ResponseCode>NOK</tmi8:ResponseCode><tmi8:ResponseError><![CDATA[%s]]></tmi8:ResponseError></tmi8:VV_TM_RES>"""

KV17_NA = """<?xml version="1.0" encoding="UTF-8"?><tmi8:VV_TM_RES xmlns:tmi8="http://bison.connekt.nl/tmi8/kv17/msg"><tmi8:SubscriberID>"""+KV17_SUBSCRIBERID+"""</tmi8:SubscriberID><tmi8:Version>"""+KV17_VERSION+"""</tmi8:Version><tmi8:DossierName>"""+KV17_DOSSIERNAME+"""</tmi8:DossierName><tmi8:Timestamp>%s</tmi8:Timestamp><tmi8:ResponseCode>NA</tmi8:ResponseCode><tmi8:ResponseError><![CDATA[%s]]></tmi8:ResponseError></tmi8:VV_TM_RES>"""

KV17_PE = """<?xml version="1.0" encoding="UTF-8"?><tmi8:VV_TM_RES xmlns:tmi8="http://bison.connekt.nl/tmi8/kv17/msg"><tmi8:SubscriberID>"""+KV17_SUBSCRIBERID+"""</tmi8:SubscriberID><tmi8:Version>"""+KV17_VERSION+"""</tmi8:Version><tmi8:DossierName>"""+KV17_DOSSIERNAME+"""</tmi8:DossierName><tmi8:Timestamp>%s</tmi8:Timestamp><tmi8:ResponseCode>PE</tmi8:ResponseCode><tmi8:ResponseError><![CDATA[%s]]></tmi8:ResponseError></tmi8:VV_TM_RES>"""
