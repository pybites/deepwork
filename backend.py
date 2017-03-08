from pprint import pprint as pp
import re
import sys
import time

import gspread
from oauth2client.service_account import ServiceAccountCredentials

GDOC = "deepworklog"


def create_client():
    scope = ['https://spreadsheets.google.com/feeds']
    creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
    return gspread.authorize(creds)


def get_sheet():
    client = create_client()
    return client.open(GDOC).sheet1


def get_next_row(sheet):
    times = [t for t in sheet.col_values(1) if t.strip()]
    return len(times) + 1


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


def show_items():
    list_of_hashes = sheet.get_all_records()
    pp(list_of_hashes)


if __name__ == "__main__":
    sheet = get_sheet()

    if len(sys.argv) < 2:
        print('Run as {} hh:mm (activity)'.format(sys.argv[0]))
        print('\nCurrently in gdoc:')
        show_items()
        sys.exit(1)

    now = int(time.time())
    entered_time = sys.argv[1]
    seconds = convert_time(entered_time)
    activity = sys.argv[2] if len(sys.argv) > 2 else ''
    row = [now, seconds, activity]

    next_row = get_next_row(sheet)
    sheet.insert_row(row, next_row)

    show_items()
