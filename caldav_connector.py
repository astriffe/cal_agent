# -*- coding: utf-8 -*-

import caldav
import time
import datetime
from dateutil.parser import parse
import logging


class CalDavConnector:
    __timestamp_format = '%Y%m%dT%H%M%S'

    __vtimezone = ("""BEGIN:VTIMEZONE
TZID:Europe/Zurich
X-LIC-LOCATION:Europe/Zurich
BEGIN:DAYLIGHT
TZOFFSETFROM:+0100
TZOFFSETTO:+0200
TZNAME:CEST
DTSTART:19700329T020000
END:DAYLIGHT
BEGIN:STANDARD
TZOFFSETFROM:+0200
TZOFFSETTO:+0100
TZNAME:CET
DTSTART:19701025T030000
RRULE:FREQ=YEARLY;BYDAY=-1SU;BYMONTH=10
END:STANDARD
END:VTIMEZONE""")

    __ical_todo_template = ("""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//striffeler/caldavagent//EN
{0}
BEGIN:VTODO
CREATED:{1}
LAST-MODIFIED:{1}
DTSTAMP:{1}
UID:{2}@calagent.striffeler.ch
SUMMARY:{3}
DESCRIPTION:{4}
STATUS:NEEDS-ACTION
CLASS:PUBLIC
END:VTODO
END:VCALENDAR""")

    __ical_event_template = ("""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//striffeler/caldavagent//EN
{0}
BEGIN:VEVENT
CREATED:{1}
LAST-MODIFIED:{1}
DTSTAMP:{1}
UID:{2}@calagent.striffeler.ch
SUMMARY:{3}
DESCRIPTION:{4}
DTSTART:{5}
DTEND:{6}
CLASS:PUBLIC
END:VEVENT
END:VCALENDAR""")

    def __init__(self, configuration):
        self.configuration = configuration
        self.url = """https://{0}:{1}@{2}/{3}""".format(self.configuration['caldav_username'],
                                                        self.configuration['caldav_password'],
                                                        self.configuration['caldav_hostname'],
                                                        self.configuration['caldav_server_path'])

    def add_todo(self, summary='', description='', author='unknown'):

        current_time = datetime.datetime.now().strftime(self.__timestamp_format)
        description += "\n--\nCreated by CalDav Agent on behalf of %s" % author
        description = description.replace('\n', '\\n').replace('\r', '')
        entry = self.__ical_todo_template.format(self.__vtimezone, current_time, int(time.time() * 1000000), summary,
                                                 description)

        self.write_to_caldav(entry)

    def add_appointment(self, summary='', description='', author='unknown'):

        description_parts = description.split('\n', 1)
        duration_line = description_parts[0]
        description = description_parts[1]
        if description_parts[1].startswith('calendar='):
            calendar_line = description_parts[1].split('\n', 1)[0]
            description = description_parts[1].split('\n', 1)[1]
            self.configuration['calendarname'] = calendar_line[9:].lstrip().replace('\n', '').replace('\r', '')

        start_text = duration_line.split('-')[0].strip()
        end_text = duration_line.split('-')[1].strip()

        start_date = parse(start_text).strftime(self.__timestamp_format)
        end_date = parse(end_text).strftime(self.__timestamp_format)

        current_time = datetime.datetime.now().strftime(self.__timestamp_format)
        description += "\n--\nCreated by CalDav Agent on behalf of %s" % author
        description = description.replace('\n', '\\n').replace('\r', '')

        entry = self.__ical_event_template.format(self.__vtimezone, current_time, int(time.time() * 1000000), summary,
                                                  description, start_date, end_date)
        self.write_to_caldav(entry)

    def write_to_caldav(self, entry):
        client = caldav.DAVClient(self.url)
        client.ssl_verify_cert = False
        principal = client.principal()
        calendars = principal.calendars()
        for cal in calendars:
            if cal.canonical_url.lower().endswith(self.configuration['calendarname'] + '/'):
                calendar = cal
                break
            calendar = cal

        if self.configuration['calendarname'] not in cal.canonical_url.lower():
            logging.warning('Could not write to desired calendar "%s", wrote to "%s" instead' % (calendar_name, cal))

        if 'VTODO' in entry:
            calendar.add_todo(entry)
        elif 'VEVENT' in entry:
            calendar.add_event(entry)
        else:
            logging.error('Malformed caldav entry: Neither VTODO nor VEVENT tag found')
            exit(1)
