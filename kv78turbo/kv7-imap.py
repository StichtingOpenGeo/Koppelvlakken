from gzip import GzipFile
from cStringIO import StringIO
import imaplib, email
import os.path
from secret import imap_host, imap_username, imap_password

m = imaplib.IMAP4_SSL(imap_host)
m.login(imap_username, imap_password)
m.select()

resp, items = m.search(None, 'ALL')
items = items[0].split()
for emailid in items:
    filename = 'KV7-%03d' % (int(emailid))
    if not os.path.exists(filename):
        resp, data = m.fetch(emailid, "(RFC822)")
        email_body = data[0][1]
        mail = email.message_from_string(email_body)
        if mail.get_content_maintype() != 'multipart':
            continue
        print "["+mail["From"]+"] :" + mail["Subject"]
        for part in mail.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            if part.get('Content-Disposition') is None:
                continue
            
            contents = part.get_payload(decode=True)
            contents = GzipFile('','r',0,StringIO(contents)).read()

            fp = open(filename, 'wb')
            fp.write(contents)
            fp.close()
