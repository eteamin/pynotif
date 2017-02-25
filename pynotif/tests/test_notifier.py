import unittest
import asyncio
import subprocess

import websockets


class TestCase(unittest.TestCase):
    def setUp(self):
        # Create the sandbox websocket server
        self.start_server = websockets.serve(self.sandbox_server)
        # Do notif insertion
        pass

    def test_notifier(self):
        pass
