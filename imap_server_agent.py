# -*- coding: utf-8 -*-

import imaplib
import logging
import email


class ImapServerAgent:
    def __init__(self, username, password, hostname, port=993):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password

    def fetch_by_subject(self, prefix='', delete_when_read=False):
        result = []
        imap_session = imaplib.IMAP4_SSL(self.hostname, str(self.port))
        imap_session.login(self.username, self.password)
        imap_session.select()

        typ, data = imap_session.search(None, '(UNSEEN SUBJECT "%s")' % prefix)

        if not typ == 'OK':
            logging.error('Messages for Subject <%s> could not be retrieved.' % prefix)

        for msgId in data[0].split():
            typ, msg_raw = imap_session.fetch(msgId, '(RFC822)')
            message = email.message_from_string(msg_raw[0][1])
            result.append(message)
            imap_session.store(msgId, '+FLAGS', '\\Seen')
            if delete_when_read:
                imap_session.store(msgId, '+FLAGS', '\\Deleted')

        for message in result:
            message.replace_header('Subject', email.Header.decode_header(message.get('Subject'))[0][0])
            clean_subject = message.get('Subject')[len(prefix):].lstrip()
            message.replace_header('Subject', clean_subject)

        imap_session.expunge()
        imap_session.close()
        imap_session.logout()

        return result
