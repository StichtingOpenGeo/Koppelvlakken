def stripschema(tag):
    return tag.split('}')[-1]

def reply(xml, start_response):
    start_response('200 OK', [('Content-Type', 'application/xml; charset=utf-8'), ("Content-Length",str(len(xml)))])
    return xml
