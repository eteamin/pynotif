import unittest
import json
from os import path
from threading import Thread
import time
from http.server import HTTPServer

from websocket import create_connection

import pynotif
from pynotif.src.notifier import Notifier
from pynotif.tests.sandbox_server import RequestHandler

PATH_TO_CONFIG = path.abspath(path.join(path.dirname(pynotif.__file__), '..', 'test.json'))


class TestCase(unittest.TestCase):
    def setUp(self):
        self.config = None
        self._load_config()
        self.http_server = (
            self.config.get('http_server').split(':')[0],
            int(self.config.get('http_server').split(':')[1])
        )
        http_server = Thread(target=self._http_server)
        http_server.daemon = True
        http_server.start()

        server_socket = Thread(target=self._server_socket)
        server_socket.daemon = True
        server_socket.start()

    def _load_config(self):
        with open(PATH_TO_CONFIG, 'r') as conf:
            self.config = json.load(conf)

    def _http_server(self):
        httpd = HTTPServer(self.http_server, RequestHandler)
        httpd.serve_forever()

    def _server_socket(self):
        n = Notifier(
            ws_server=self.config.get('ws_server'),
            db=self.config.get('db'),
            http_server_url=self.config.get('http_server'),
            config=None
        )
        n.setup()

    def test_client_socket(self):
        time.sleep(1)  # Wait for the ws to run
        ws = create_connection('ws://{}'.format(self.config.get('ws_server')))
        fake_identity = {
            "account": 1000,
            "session": "fake_session"
        }
        # Register
        ws.send(str(fake_identity))
        # Fetch notif
        notif = ws.recv().decode('utf-8')
        assert notif == 'Notification'
        ws.close()
