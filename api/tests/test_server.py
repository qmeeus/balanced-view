import unittest
import requests

HOST = "localhost"
API_PORT = 32597
UI_PORT = 8080

class TestServer(unittest.TestCase):

    def _test_connection(self, port):
        r = requests.get(f"http://{HOST}:{port}")

    def test_api_connection(self):
        self._test_connection(API_PORT)

    def test_ui_connection(self):
        self._test_connection(UI_PORT)


if __name__ == '__main__':
    unittest.main()
