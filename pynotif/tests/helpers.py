from http.server import BaseHTTPRequestHandler
import json

import redis


class RequestHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        raw_info = self.rfile.read(int(self.headers['Content-Length'])).decode('utf-8').replace("'", "\"")
        json_info = json.loads(raw_info)
        valid_info = {
            'account': 1000,
            'session': 'fake_session'
        }
        if json_info == valid_info:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            message = dict(ok=True, account=valid_info['account'])
            self.wfile.write(bytes(str(message), "utf8"))
            return

    def store_notification(self):
        r = redis.StrictRedis()
