from collections import namedtuple
from functools import wraps
import os
import sys
import time

from flask import Flask, abort, jsonify, make_response, request

from backend import get_sheet, get_next_row, convert_time

COMMAND = '/dw'
SLACK_DW_CMD_TOKEN = os.environ.get('SLACK_DW_CMD_TOKEN')

Entry = namedtuple('entry', 'user time seconds activity')

sheet = get_sheet()
app = Flask(__name__)


@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify({'error': 'Bad request'}), 400)


@app.route('/api/v1.0/entries', methods=['GET'])
def get_items():
    entries = sheet.get_all_records()
    return jsonify({'entries': entries})


@app.route('/api/v1.0/entries', methods=['POST'])
def post_entry():
    if not request.json or 'token' not in request.json:
        abort(400)
    token = request.json.get('token')
    if token != SLACK_DW_CMD_TOKEN:
        abort(400)
    cmd = request.json.get('command')
    user = request.json.get('user')
    text = request.json.get('text')
    if not cmd == COMMAND:
        abort(400)
    now = int(time.time())
    try:
        seconds = convert_time(text)
    except ValueError as err:
        abort(400)
    text_fields = text.split(' ', 1)
    if len(text_fields) > 1:
        activity = ' '.join(text_fields[1:])
    else:
        activity = ''
    row = [user, now, seconds, activity]
    next_row = get_next_row(sheet)
    sheet.insert_row(row, next_row)
    entry = Entry(*row)
    return jsonify(entry), 201


if __name__ == '__main__':
    app.run(debug=True)
