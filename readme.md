# CalDav Agent
This tool provides an interface to add Todo or Calendar items to your CalDav server by sending e-mails. For the moment, it has only been tested with owncloud server.


Please feel free to fork the project and send me pull requests with your bug fixes or enhancements.

## Usage
The Cal Agent in its current configuration only runs once per invocation. Hence, to parse your emails on a regular basis, I suggest to use your systems' scheduler. While it would be easy to run an infinite loop in python itself, it seems much more appealing to me to use cronjobs instead.

All available command-line parameters are optional. If you don't add any option, the tool assumes your configuration file is named `config.ini` and lies in the same folder as `cal_agent.py`. The default profile is called - guess what - `default`.

If you want to specify your own config or run several configurations alongside, you can specifiy files and profiles, for instance:

```
python cal_agent.py --config /home/astriffe/config.ini --profile owncloud
```


The correct parsing of the e-mail messages relies on some conventions on how these messages are structured:

### Todo
Subject prefix: 'TODO'

E-Mail body: Description

### Calendar
Subject prefix: 'CAL'

E-Mail Body:
* first line: <start> - <end> (mandatory, delimited by a dash)
* second line*: calendar=<calendarName> (optional)

The delimiter for the can be defined in the imap section of the configuration file using the property 
All entries will be suffixed with the sender's name and e-mail address.

## Configuration
The parameters for both IMAP and CalDav server connections can be specified in a separate configuration file. On application start, this file can be specified. This allows for storing the configuration with probably sensitive password data at a protected place. The following configuration properties are available, all except those marked with an asterix are mandatory. I'll quickly explain the non-trivial ones:
* `imap_username` 
* `imap_password`
* `imap_hostname`
* `imap_port`
* `caldav_username`
* `caldav_password`
* `caldav_port`
* `caldav_server_path`: The path on which your server provides the caldav interface. For owncloud, this should equal 'remote.php/caldav'
* `delete_when_read`\*: Decide whether to delete processed messages on the imap server or not. Note: To avoid create multiple entries from one message, only unseen messages are processed and immediately marked 'seen' afterwards.
* `date_delimiter`\*: The delimiter between start and end time of an event. Please make sure this character does not conflict with the date format.
* `calendarname`\*: The name of the calendar your tasks are stored in, as well as the events if you do not specify a different calendar name.

# Disclaimer
Use at own risk, protect against spam and get lucky :)
	


