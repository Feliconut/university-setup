from datetime import datetime
from pathlib import Path

def get_week(d=datetime.today()):
    return (int(d.strftime("%W")) + 52 - 5) % 52

# default is 'primary', if you are using a separate calendar for your course schedule,
# your calendarId (which you can find by going to your Google Calendar settings, selecting
# the relevant calendar and scrolling down to Calendar ID) probably looks like
# xxxxxxxxxxxxxxxxxxxxxxxxxg@group.calendar.google.com
# example:
# USERCALENDARID = 'xxxxxxxxxxxxxxxxxxxxxxxxxg@group.calendar.google.com'
USERCALENDARID = 'primary'
ROOT = Path('~/univ').expanduser()
CURRENT_SEMESTER_SYMLINK = Path('~/univ/current_semester').expanduser()
CURRENT_COURSE_SYMLINK = Path('~/univ/current_course').expanduser()
CURRENT_COURSE_ROOT = CURRENT_COURSE_SYMLINK.resolve()
CURRENT_COURSE_WATCH_FILE = Path('/tmp/current_course').resolve()
DATE_FORMAT = '%a %d %b %Y %H:%M'


# auto-check of paths
if not ROOT.exists():
    raise Exception('Root path does not exist: {}'.format(ROOT))
elif not CURRENT_SEMESTER_SYMLINK.exists():
    raise Exception('Current semester path does not exist: {}'.format(CURRENT_SEMESTER_SYMLINK))
elif not CURRENT_COURSE_SYMLINK.exists():
    raise Exception('Current course path does not exist: {}'.format(CURRENT_COURSE_SYMLINK))
