from pyicloud import PyiCloudService
from operator import itemgetter
import datetime
import click

last_events = []

def renderCalendarEvents(events):
  global last_events
  events = sorted(events, key=itemgetter('startDate'))
  if (events != last_events):
    print 'Refreshing display...'

    print '#EVENTS'
    for event in events:
      print event['title']
      if 'startDate' in event:
        print '\t+', event['startDate']
      if 'endDate' in event:
        print '\t-', event['endDate']
      if 'location' in event:
        print '\t@', event['location']

    last_events = events
  else:
    print 'No change.'

email = click.prompt('iCloud email')
password = click.prompt('iCloud password', hide_input=True)
print 'Authenticating with iCloud...'
api = PyiCloudService(email, password)
if api.requires_2fa:
  print "Two-factor authentication required. Your trusted devices are:"

  devices = api.trusted_devices
  for i, device in enumerate(devices):
    print "  %s: %s" % (i, device.get('deviceName',
      "SMS to %s" % device.get('phoneNumber')))

  device = click.prompt('Which device would you like to use?', default=0)
  device = devices[device]
  if not api.send_verification_code(device):
    print "Failed to send verification code"
    sys.exit(1)

  code = click.prompt('Please enter verification code')
  if not api.validate_verification_code(device, code):
    print 'Failed to verify verification code'
    sys.exit(1)

import time
starttime=0
while True:
  try:
    events = api.calendar.events(datetime.date.today(), datetime.date.today())
    renderCalendarEvents(events)
  except KeyError:
    renderCalendarEvents([])
  except Exception as err:
    print err
    if err == 'Invalid global session':
      api = PyiCloudService(email, password)

  time_to_wait = 300.0 - ((time.time() - starttime) % 300.0)
  print 'Waiting %ds before update...' % time_to_wait
  time.sleep(time_to_wait)
