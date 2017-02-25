import unittest
import threading

from pynotif.src.notifier import Notifier


class TestCase(unittest.TestCase):
    def setUp(self):
        # Create the sandbox websocket server using the test db (15)
        self.db = 15
        self.host = '127.0.0.1'
        self.port = 6767
        self.thread = threading.Thread(target=self.sandbox)
        self.thread.daemon = True
        self.thread.start()

        # Push some data
        

    def sandbox(self):
        Notifier(self.host, self.port, self.db)

    def test_notifier(self):
        print(self.thread.getName())
