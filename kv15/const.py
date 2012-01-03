ISO_TIME = "%Y-%m-%dT%H:%M:%S+0200"

KV15_SUBSCRIBERID = "openOV"
KV15_VERSION = "BISON 8.1.0.0"
KV15_DOSSIERNAME = "KV15messages"

KV15_PSHOST = "kv15.xmpp.openov.nl"

KV15_OK = """<?xml version="1.0" encoding="UTF-8"?><tmi8:VV_TM_RES xmlns:tmi8="http://bison.connekt.nl/tmi8/kv6/msg"><tmi8:SubscriberID>"""+KV15_SUBSCRIBERID+"""</tmi8:SubscriberID><tmi8:Version>"""+KV15_VERSION+"""</tmi8:Version><tmi8:DossierName>"""+KV15_DOSSIERNAME+"""</tmi8:DossierName><tmi8:Timestamp>%s</tmi8:Timestamp><tmi8:ResponseCode>OK</tmi8:ResponseCode></tmi8:VV_TM_RES>"""

KV15_SE = """<?xml version="1.0" encoding="UTF-8"?><tmi8:VV_TM_RES xmlns:tmi8="http://bison.connekt.nl/tmi8/kv6/msg"><tmi8:SubscriberID>"""+KV15_SUBSCRIBERID+"""</tmi8:SubscriberID><tmi8:Version>"""+KV15_VERSION+"""</tmi8:Version><tmi8:DossierName>"""+KV15_DOSSIERNAME+"""</tmi8:DossierName><tmi8:Timestamp>%s</tmi8:Timestamp><tmi8:ResponseCode>SE</tmi8:ResponseCode><tmi8:ResponseError><![CDATA[%s]]></tmi8:ResponseError></tmi8:VV_TM_RES>"""

KV15_NOK = """<?xml version="1.0" encoding="UTF-8"?><tmi8:VV_TM_RES xmlns:tmi8="http://bison.connekt.nl/tmi8/kv6/msg"><tmi8:SubscriberID>"""+KV15_SUBSCRIBERID+"""</tmi8:SubscriberID><tmi8:Version>"""+KV15_VERSION+"""</tmi8:Version><tmi8:DossierName>"""+KV15_DOSSIERNAME+"""</tmi8:DossierName><tmi8:Timestamp>%s</tmi8:Timestamp><tmi8:ResponseCode>NOK</tmi8:ResponseCode><tmi8:ResponseError><![CDATA[%s]]></tmi8:ResponseError></tmi8:VV_TM_RES>"""

KV15_NA = """<?xml version="1.0" encoding="UTF-8"?><tmi8:VV_TM_RES xmlns:tmi8="http://bison.connekt.nl/tmi8/kv6/msg"><tmi8:SubscriberID>"""+KV15_SUBSCRIBERID+"""</tmi8:SubscriberID><tmi8:Version>"""+KV15_VERSION+"""</tmi8:Version><tmi8:DossierName>"""+KV15_DOSSIERNAME+"""</tmi8:DossierName><tmi8:Timestamp>%s</tmi8:Timestamp><tmi8:ResponseCode>NA</tmi8:ResponseCode><tmi8:ResponseError><![CDATA[%s]]></tmi8:ResponseError></tmi8:VV_TM_RES>"""

KV15_PE = """<?xml version="1.0" encoding="UTF-8"?><tmi8:VV_TM_RES xmlns:tmi8="http://bison.connekt.nl/tmi8/kv6/msg"><tmi8:SubscriberID>"""+KV15_SUBSCRIBERID+"""</tmi8:SubscriberID><tmi8:Version>"""+KV15_VERSION+"""</tmi8:Version><tmi8:DossierName>"""+KV15_DOSSIERNAME+"""</tmi8:DossierName><tmi8:Timestamp>%s</tmi8:Timestamp><tmi8:ResponseCode>PE</tmi8:ResponseCode><tmi8:ResponseError><![CDATA[%s]]></tmi8:ResponseError></tmi8:VV_TM_RES>"""

KV15_IC = """<?xml version="1.0" encoding="UTF-8"?><tmi8:VV_TM_RES xmlns:tmi8="http://bison.connekt.nl/tmi8/kv6/msg"><tmi8:SubscriberID>"""+KV15_SUBSCRIBERID+"""</tmi8:SubscriberID><tmi8:Version>"""+KV15_VERSION+"""</tmi8:Version><tmi8:DossierName>"""+KV15_DOSSIERNAME+"""</tmi8:DossierName><tmi8:Timestamp>%s</tmi8:Timestamp><tmi8:ResponseCode>IC</tmi8:ResponseCode><tmi8:ResponseError><![CDATA[%s]]></tmi8:ResponseError></tmi8:VV_TM_RES>"""

KV15_AE = """<?xml version="1.0" encoding="UTF-8"?><tmi8:VV_TM_RES xmlns:tmi8="http://bison.connekt.nl/tmi8/kv6/msg"><tmi8:SubscriberID>"""+KV15_SUBSCRIBERID+"""</tmi8:SubscriberID><tmi8:Version>"""+KV15_VERSION+"""</tmi8:Version><tmi8:DossierName>"""+KV15_DOSSIERNAME+"""</tmi8:DossierName><tmi8:Timestamp>%s</tmi8:Timestamp><tmi8:ResponseCode>AE</tmi8:ResponseCode><tmi8:ResponseError><![CDATA[%s]]></tmi8:ResponseError></tmi8:VV_TM_RES>"""
