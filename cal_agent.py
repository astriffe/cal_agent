# -*- coding: utf-8 -*-

import sys
import configparser
import logging
from optparse import OptionParser

from imap_server_agent import ImapServerAgent
from caldav_connector import CalDavConnector


class CalDavAgent:
    def __init__(self):
        self.config = {}

    def perform_run(self, configuration_file='./config.ini', profile='default'):

        self.load_configuration(configuration_file, profile)
        mail = ImapServerAgent(self.config['imap_username'], self.config['imap_password'], self.config['imap_hostname'],
                               self.config['imap_port'])
        todo_items = mail.fetch_by_subject('TODO', self.config['deleteWhenRead'])
        calendar_items = mail.fetch_by_subject('CAL', self.config['deleteWhenRead'])

        caldav = CalDavConnector(self.config)

        for todo in todo_items:
            caldav.add_todo(todo['Subject'], todo.get_payload(), todo['From'])

        for event in calendar_items:
            caldav.add_appointment(event['Subject'], event.get_payload(), event['From'])

    @staticmethod
    def load_text_body(email):
        body = ""
        for part in email.walk():
            if part.get_content_type() == 'text/plain':
                body += str(part)
            else:
                logging.warning('Only text/plain is allowed, received %s' % (part.get_content_type()))

        return body

    def load_configuration(self, configuration_file='./config.ini', profile='default'):
        configuration = configparser.ConfigParser()
        configuration.read(configuration_file)

        for option in ['imap_username', 'imap_password', 'imap_hostname', 'imap_port']:
            try:
                self.config[option] = configuration.get(profile, option)
            except NameError:
                logging.error('Mail Server Configuration file does not provide expected property: %s' % option)
                sys.exit(1)
            try:
                self.config['deleteWhenRead'] = configuration.getboolean(profile, 'delete_when_read')
            except NameError:
                self.config['deleteWhenRead'] = False
            try:
                self.config['dateDelimiter'] = configuration.get(profile, 'date_delimiter').strip()
            except NameError:
                self.config['dateDelimiter'] = '-'

        for option in ['caldav_username', 'caldav_password', 'caldav_hostname', 'caldav_port', 'calendarname',
                       'caldav_server_path']:
            try:
                self.config[option] = configuration.get(profile, option)
            except NameError:
                logging.error('Mail Server Configuration file does not provide expected property: %s' % option)
                exit(1)


if __name__ == "__main__":
    parser = OptionParser(usage="""\
Check IMAP Server for emails and write them to a given CalDav server, either as TODOs or as EVENTs. """)

    parser.add_option('-c', '--config',
                      dest='config',
                      default='./config.ini',
                      help='The file containing the configuration for both IMAP and CalDav Servers. ' +
                           'You can find a sample configuration in the application root.')

    parser.add_option('--profile',
                      dest='profile',
                      default='default',
                      help='The name of your configuration profile')

    opts, remainder = parser.parse_args()

    if not opts.config:
        parser.print_help()
        exit(1)

    agent = CalDavAgent()
    agent.perform_run(opts.config, opts.profile)
    exit(0)
