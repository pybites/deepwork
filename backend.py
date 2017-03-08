import os
import re
import sys
import time

import pygsheets

GDOC = "deepworklog"
USER = os.environ.get('SLACK_DW_USER')


def get_sheet():
    gc = pygsheets.authorize(service_file='client_secret.json')
    sh = gc.open(GDOC)
    return sh.sheet1


def calc_seconds(hours, minutes):
    return hours * 60 * 60 + minutes * 60


def convert_time(time):
    time = str(time)
    if re.match(r'^\d+$', time):
        return int(time) * 60 * 60
    time = time.split(' ', 1)[0]
    if ':' and time.count(':') == 1:
        hours, minutes = time.split(':')
        try:
            hours = int(hours)
            minutes = int(minutes)
        except ValueError('cannot convert hours / minutes to ints'):
            raise
        return calc_seconds(hours, minutes)
    raise ValueError('not a supported time format, supported = digit or hh:mm')



if __name__ == "__main__":
    wks = get_sheet()

    if len(sys.argv) < 2:
        print('Run as {} hh:mm (activity)'.format(sys.argv[0]))
        print('\nCurrently in gdoc:')
        print([i[:4] for i in (list(wks)[1:])])

    else:
        now = int(time.time())
        entered_time = sys.argv[1]
        seconds = convert_time(entered_time)
        activity = sys.argv[2] if len(sys.argv) > 2 else ''
        row = [USER, now, seconds, activity]
        print(row)
        wks.insert_rows(row=2, number=1, values=row)
