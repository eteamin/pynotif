import unittest
import json
from os import path
from threading import Thread
from threading import Event
import time
from http.server import HTTPServer

from websocket import create_connection
import redis

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
        self.fake_identity = {
            "account": str(1000),
            "session": "fake_session"
        }
        self.connection_closed = Event()
        http_server = Thread(target=self._http_server)
        http_server.daemon = True
        http_server.start()

        server_socket = Thread(target=self._server_socket)
        server_socket.daemon = True
        server_socket.start()

        redis_handler = Thread(target=self._redis_handler)
        redis_handler.daemon = True
        redis_handler.start()

    def _load_config(self):
        with open(PATH_TO_CONFIG, 'r') as conf:
            self.config = json.load(conf)

    def _http_server(self):
        httpd = HTTPServer(self.http_server, RequestHandler)
        httpd.serve_forever()

    def _server_socket(self):
        n = Notifier(config=self.config)
        n.serve()

    def _redis_handler(self):
        r = redis.StrictRedis(db=self.config.get('db'))
        r.set(self.fake_identity.get('account'), 'Notification')
        self.connection_closed.wait()  # Wait for the other thread to close the first connection
        r.set(self.fake_identity.get('account'), 'Pending notification')

    def test_client_socket(self):
        time.sleep(1)  # Wait for the ws to run

        ws = create_connection('ws://{}'.format(self.config.get('ws_server')), header=self.fake_identity)
        notif = ws.recv()
        assert notif == 'Notification'
        ws.close()
        self.connection_closed.set()
        # Testing pending notifications. _redis_handler stores two notifications

        # So we try yo connect and receive the pending notification
        ws = create_connection('ws://{}'.format(self.config.get('ws_server')), header=self.fake_identity)
        notif = ws.recv()
        assert notif == 'Pending notification'
        ws.close()

        # No auth
        ws = create_connection('ws://{}'.format(self.config.get('ws_server')))
        notif = ws.recv()
        assert notif == 'Auth failed!'
        ws.close()
