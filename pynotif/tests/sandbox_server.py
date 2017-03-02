from http.server import BaseHTTPRequestHandler
import json
from os import path

import pynotif
import redis


PATH_TO_CONFIG = path.abspath(path.join(path.dirname(pynotif.__file__), '..', 'test.json'))


class RequestHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        raw_info = self.rfile.read(int(self.headers['Content-Length'])).decode('utf-8').replace("'", "\"")
        json_info = json.loads(raw_info)
        self.valid_info = {
            'account': 1000,
            'session': 'fake_session'
        }
        self._load_config()
        if json_info == self.valid_info:
            self._store_notification()  # Meanwhile a notif is set
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            message = '{"ok":"True", "account":"%s"}' % self.valid_info['account']
            self.wfile.write(bytes(message, "utf8"))
            return

    def _store_notification(self):
        r = redis.StrictRedis(db=self.config.get('db'))
        r.set(self.valid_info['account'], 'Notification')

    def _load_config(self):
        with open(PATH_TO_CONFIG, 'r') as conf:
            self.config = json.load(conf)
