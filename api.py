from collections import namedtuple
import os
import time

from flask import Flask, jsonify, abort, make_response, request

from backend import get_sheet, get_next_row, convert_time

BAD_REQUEST = 'Bad request'
COMMAND = '/dw'
SLACK_DW_CMD_TOKEN = os.environ.get('SLACK_DW_CMD_TOKEN')

Entry = namedtuple('entry', 'user time seconds activity')

sheet = get_sheet()
app = Flask(__name__)


@app.errorhandler(400)
def bad_request(error):
    msg = '{}: {}'.format(BAD_REQUEST, error)
    return make_response(jsonify({'message': msg}), 400)


@app.route('/api/v1.0/entries', methods=['GET'])
def get_items():
    entries = sheet.get_all_records()
    return jsonify({'entries': entries})


@app.route('/api/v1.0/entries', methods=['POST'])
def post_entry():
    if not request.json or 'token' not in request.json:
        abort(400, 'missing parameters')
    token = request.form.get('token')
    cmd = request.form.get('command')
    user = request.form.get('user')
    text = request.form.get('text')
    if token != SLACK_DW_CMD_TOKEN:
        abort(400, 'wrong slack token')
    if not cmd == COMMAND:
        abort(400, 'not the right command')
    now = int(time.time())
    try:
        seconds = convert_time(text)
    except ValueError as err:
        abort(400, err)
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
