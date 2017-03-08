from collections import namedtuple
from functools import wraps
import os
import time

from flask import Flask, abort, jsonify, make_response, request, Response

from backend import get_sheet, get_next_row, convert_time

COMMAND = '/dw'
SLACK_DW_CMD_TOKEN = os.environ.get('SLACK_DW_CMD_TOKEN')
SLACK_DW_USER = os.environ.get('SLACK_DW_USER')
SLACK_DW_PW = os.environ.get('SLACK_DW_PW')

Entry = namedtuple('entry', 'user time seconds activity')

sheet = get_sheet()
app = Flask(__name__)


def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    print(username)
    print(password)
    print(SLACK_DW_USER)
    print(SLACK_DW_PW)
    print( username == SLACK_DW_USER and password == SLACK_DW_PW)
    return username == SLACK_DW_USER and password == SLACK_DW_PW


def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'}
    )


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated


@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify({'error': 'Bad request'}), 400)


@app.route('/api/v1.0/entries', methods=['GET'])
@requires_auth
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
