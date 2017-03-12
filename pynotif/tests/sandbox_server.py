from http.server import BaseHTTPRequestHandler
import json
from base64 import b64decode
from os import path
import time

import pynotif
from pyDes import triple_des
import redis


PATH_TO_CONFIG = path.abspath(path.join(path.dirname(pynotif.__file__), '..', 'test.json'))
OFFSET = 0


class RequestHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        global OFFSET
        self._load_config()
        self._authorize()
        if OFFSET == 0:  # First time client connects store, else dismiss the storage of `Notification`
            self._store_notification('Notification')  # Meanwhile a notif is set
            OFFSET += 1
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        message = '{"ok":"True", "account":"%s"}' % self.valid_info['account']
        self.wfile.write(bytes(message, "utf8"))

        if OFFSET == 1:
            time.sleep(3)  # Wait for client to dismiss
            self._store_notification('Pending notification')  # So the second time he connects he fetches this
            OFFSET += 1  # So the second time it wont trigger again

    def _authorize(self):
        json_info = {
            'account': self.headers.get('account'),
            'session': self.headers.get('session'),
        }
        self.valid_info = {
            'account': '1000',
            'session': 'fake_session'
        }
        token = b64decode(bytes(self.headers.get('token')[len("b'"):-len("'")], encoding="utf-8"))
        auth_message = triple_des(self.config.get('auth_secret_key')).decrypt(token, padmode=2).decode()
        assert auth_message == self.config.get('auth_message')
        assert json_info == self.valid_info

    def _store_notification(self, notif):
        r = redis.StrictRedis(db=self.config.get('db'))
        r.set(self.valid_info['account'], notif)

    def _load_config(self):
        with open(PATH_TO_CONFIG, 'r') as conf:
            self.config = json.load(conf)
