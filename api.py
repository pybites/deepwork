from collections import namedtuple
from functools import wraps
import os
import time

from flask import Flask, abort, jsonify, make_response, request, Response
import pygsheets

from backend import get_sheet, convert_time

COMMAND = '/dw'
SLACK_DW_CMD_TOKEN = os.environ.get('SLACK_DW_CMD_TOKEN')
SLACK_DW_USER = os.environ.get('SLACK_DW_USER')
SLACK_DW_PW = os.environ.get('SLACK_DW_PW')

Entry = namedtuple('entry', 'user time seconds activity')

wks = get_sheet()
app = Flask(__name__)


def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
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
    entries = [i[:4] for i in (list(wks)[1:])]
    return jsonify({'entries': entries})


@app.route('/api/v1.0/entries', methods=['POST'])
def post_entry():
    # slack uses request.form, not request.json!
    print('request.form data: ', request.form)
    if not request.form or 'token' not in request.form:
        print('No token provided')
        abort(400)
    token = request.form.get('token')
    if token != SLACK_DW_CMD_TOKEN:
        print('Wrong slack token')
        abort(400)
    cmd = request.form.get('command')
    user = request.form.get('user_name')
    text = request.form.get('text')
    channel_name = request.form.get('channel_name')
    if not cmd == COMMAND:
        print('Wrong command')
        abort(400)
    now = int(time.time())
    try:
        seconds = convert_time(text)
    except ValueError as err:
        print('Exception converting time: ', err)
        abort(400)
    text_fields = text.split(' ', 1)
    if len(text_fields) > 1:
        activity = ' '.join(text_fields[1:])
    else:
        activity = channel_name
    row = [user, now, seconds, activity]
    wks.append_row(start='A1', values=row)
    entry = Entry(*row)
    return jsonify(entry), 201


if __name__ == '__main__':
    app.run(debug=True)
