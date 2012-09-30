ISO_TIME = "%Y-%m-%dT%H:%M:%S+0200"

KV6_SUBSCRIBERID = "openOV"
KV6_VERSION = "BISON 8.1.0.0"
KV6_DOSSIERNAME = "KV6posinfo"

KV6_PSHOST = "kv6.xmpp.openov.nl"

KV6_OK = """<?xml version="1.0" encoding="UTF-8"?><tmi8:VV_TM_RES xmlns:tmi8="http://bison.connekt.nl/tmi8/kv6/msg"><tmi8:SubscriberID>"""+KV6_SUBSCRIBERID+"""</tmi8:SubscriberID><tmi8:Version>"""+KV6_VERSION+"""</tmi8:Version><tmi8:DossierName>"""+KV6_DOSSIERNAME+"""</tmi8:DossierName><tmi8:Timestamp>%s</tmi8:Timestamp><tmi8:ResponseCode>OK</tmi8:ResponseCode></tmi8:VV_TM_RES>"""

KV6_SE = """<?xml version="1.0" encoding="UTF-8"?><tmi8:VV_TM_RES xmlns:tmi8="http://bison.connekt.nl/tmi8/kv6/msg"><tmi8:SubscriberID>"""+KV6_SUBSCRIBERID+"""</tmi8:SubscriberID><tmi8:Version>"""+KV6_VERSION+"""</tmi8:Version><tmi8:DossierName>"""+KV6_DOSSIERNAME+"""</tmi8:DossierName><tmi8:Timestamp>%s</tmi8:Timestamp><tmi8:ResponseCode>SE</tmi8:ResponseCode><tmi8:ResponseError><![CDATA[%s]]></tmi8:ResponseError></tmi8:VV_TM_RES>"""

KV6_NOK = """<?xml version="1.0" encoding="UTF-8"?><tmi8:VV_TM_RES xmlns:tmi8="http://bison.connekt.nl/tmi8/kv6/msg"><tmi8:SubscriberID>"""+KV6_SUBSCRIBERID+"""</tmi8:SubscriberID><tmi8:Version>"""+KV6_VERSION+"""</tmi8:Version><tmi8:DossierName>"""+KV6_DOSSIERNAME+"""</tmi8:DossierName><tmi8:Timestamp>%s</tmi8:Timestamp><tmi8:ResponseCode>NOK</tmi8:ResponseCode><tmi8:ResponseError><![CDATA[%s]]></tmi8:ResponseError></tmi8:VV_TM_RES>"""

KV6_NA = """<?xml version="1.0" encoding="UTF-8"?><tmi8:VV_TM_RES xmlns:tmi8="http://bison.connekt.nl/tmi8/kv6/msg"><tmi8:SubscriberID>"""+KV6_SUBSCRIBERID+"""</tmi8:SubscriberID><tmi8:Version>"""+KV6_VERSION+"""</tmi8:Version><tmi8:DossierName>"""+KV6_DOSSIERNAME+"""</tmi8:DossierName><tmi8:Timestamp>%s</tmi8:Timestamp><tmi8:ResponseCode>NA</tmi8:ResponseCode><tmi8:ResponseError><![CDATA[%s]]></tmi8:ResponseError></tmi8:VV_TM_RES>"""

KV6_PE = """<?xml version="1.0" encoding="UTF-8"?><tmi8:VV_TM_RES xmlns:tmi8="http://bison.connekt.nl/tmi8/kv6/msg"><tmi8:SubscriberID>"""+KV6_SUBSCRIBERID+"""</tmi8:SubscriberID><tmi8:Version>"""+KV6_VERSION+"""</tmi8:Version><tmi8:DossierName>"""+KV6_DOSSIERNAME+"""</tmi8:DossierName><tmi8:Timestamp>%s</tmi8:Timestamp><tmi8:ResponseCode>PE</tmi8:ResponseCode><tmi8:ResponseError><![CDATA[%s]]></tmi8:ResponseError></tmi8:VV_TM_RES>"""

PS_PUSH = "tcp://127.0.0.1:6100"
