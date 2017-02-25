import unittest
from threading import Thread
from http.server import HTTPServer

from websocket import create_connection

from pynotif.tests.helpers import RequestHandler


class TestCase(unittest.TestCase):
    def setUp(self):
        http_server = Thread(target=self._http_server)
        http_server.daemon = True

        client_socket = Thread()

    def _http_server(self):
        server_address = ('127.0.0.1', 8081)
        httpd = HTTPServer(server_address, RequestHandler)
        httpd.serve_forever()

    def client_socket(self):
        ws = create_connection("ws://echo.websocket.org/")
        ws.send("Hello, World")
        result = ws.recv()
        ws.close()