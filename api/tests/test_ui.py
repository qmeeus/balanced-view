import requests
import unittest
import warnings
import os
from queue import Queue
from threading import Thread

from tests.utils import load_texts
from api.utils.logger import logger

try:
    from bs4 import BeautifulSoup
except:
    os.system('pip install bs4')
    from bs4 import BeautifulSoup

# UI_LOCATION = "http://localhost:9999"
UI_LOCATION = "http://cardia.cs.kuleuven.be:8080"


class TestUI(unittest.TestCase):

    N_WORKERS = 12

    def __init__(self, *args, **kwargs):
        r = requests.get(UI_LOCATION)
        if not r.status_code == 200:
            raise ConnectionError(f"The UI was not found at {UI_LOCATION}")
        super(TestUI, self).__init__(*args, **kwargs)

    def test_ui(self):
        logger.debug(f"Start ui test @ {UI_LOCATION}")
        csrf_token = self._get_csrf_token()
        assert bool(csrf_token)

        for i, (_, text) in enumerate(load_texts()):
            title = text.strip().split('\n')[0]
            msg = f"Text #{i}: {title[:50]}... "
            n_results = self._test_post_request(text, csrf_token)
            logger.debug(msg + str(n_results) + " results")

    def test_ui_under_pressure(self):
        queue = Queue()
        csrf_token = self._get_csrf_token()

        def threader():
            while True:
                text = queue.get()
                self._test_post_request(text, csrf_token)
                queue.task_done()

        for _ in range(self.N_WORKERS):
            t = Thread(target=threader)
            t.daemon = True
            t.start()

        for _, text in load_texts():
            queue.put(text)

        queue.join()

    def _get_csrf_token(self):
        resp = requests.get(UI_LOCATION)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        return soup.find("input", {"id": "csrf_token"}).get("value")

    def _test_post_request(self, text, csrf_token):
        params = {"text": text, "csrf_token": csrf_token}
        resp = requests.post(UI_LOCATION, params)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        graph_container = soup.find("div", {"id": "graph-container"})
        if not graph_container:
            warnings.warn("No graph found")
        articles = soup.find_all("div", {"class": "thumbnail article"})
        return len(articles)


if __name__ == '__main__':
    unittest.main()
