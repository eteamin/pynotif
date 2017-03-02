import unittest
from threading import Thread
from http.server import HTTPServer

from websocket import create_connection

from pynotif.src.notifier import Notifier
from pynotif.tests.helpers import RequestHandler


class TestCase(unittest.TestCase):
    def setUp(self):
        self.http_server_address = ('127.0.0.1', 8081)
        self.socket_server_address = ('127.0.0.1', 8082)
        self.db = 15

        http_server = Thread(target=self._http_server)
        http_server.daemon = True
        http_server.start()

        server_socket = Thread(target=self._server_socket)
        server_socket.daemon = True
        server_socket.start()

    def _http_server(self):
        httpd = HTTPServer(self.http_server_address, RequestHandler)
        httpd.serve_forever()

    def _server_socket(self):
        Notifier(
            host=self.socket_server_address[0],
            port=self.socket_server_address[1],
            db=self.db,
            server_url='{}:{}'.format(self.http_server_address[0], self.http_server_address[1]),
            config=None
        )

    def test_client_socket(self):
        ws = create_connection('ws://{}:{}'.format(self.socket_server_address[0], self.socket_server_address[1]))
        fake_identity = {
            "account": 1000,
            "session": "fake_session"
        }
        ws.send(str(fake_identity))
        assert ws.recv() is not None
        ws.close()
