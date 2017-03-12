from http.server import BaseHTTPRequestHandler
import json
from base64 import b64decode
from os import path
import time

import pynotif
from pyDes import triple_des

PATH_TO_CONFIG = path.abspath(path.join(path.dirname(pynotif.__file__), '..', 'test.json'))


class RequestHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        self._load_config()
        self._authorize()
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        message = '{"ok":"True", "account":"%s"}' % self.valid_info['account']
        self.wfile.write(bytes(message, "utf8"))

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

    def _load_config(self):
        with open(PATH_TO_CONFIG, 'r') as conf:
            self.config = json.load(conf)
