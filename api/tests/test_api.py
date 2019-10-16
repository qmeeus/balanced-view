import unittest
import requests
import json
from operator import itemgetter
import os
from threading import Thread
from queue import Queue

from tests.test_articles import Meta
from tests.utils import load_texts, load_keywords
from api.utils.logger import logger


# API_LOCATION = f"http://localhost:{os.environ['FLASK_RUN_PORT']}"
API_LOCATION = f"http://localhost:32597"


class TestArticleEndpoint(unittest.TestCase, Meta):

    ENDPOINT = API_LOCATION + "/articles"

    def _make_request(self, params):
        resp = requests.post(self.ENDPOINT, json=params)
        try:
            return resp.json()
        except Exception as err:
            logger.exception(err)
            logger.debug(resp.text)
            raise err


class TestAnalyseEndpoint(unittest.TestCase):

    ENDPOINT = API_LOCATION + "/analyse"
    N_WORKERS = 12

    DEFAULT_PARAMS = {
        'related': True,
        'search_languages': ['fr', 'en', 'nl'],
        'groupby_options': {
            "key": "language",
            "default": "Other",
            "groups": [
                {"name": "French", "value": "fr"},
                {"name": "Dutch", "value": "nl"},
            ],
            "orderby": "relevance",
            "reverse": True,
            "max_results_per_group": 3
        }
    }

    def test_under_pressure(self):
        queue = Queue()

        def threader():
            while True:
                params = queue.get()
                self._make_request(params)
                queue.task_done()

        for _ in range(self.N_WORKERS):
            t = Thread(target=threader)
            t.daemon = True
            t.start()

        params = self.DEFAULT_PARAMS.copy()
        for _, text in load_texts():
            params.update({'input_text': text})
            queue.put(params)

        queue.join()

    def test_endpoint(self):

        params = self.DEFAULT_PARAMS.copy()
        for _, text in load_texts():
            params.update({'input_text': text})
            self._test_request(params)

    def _test_request(self, params):
        response = self._make_request(params)
        if "message" in response:
            logger.debug(response)
            return
        self.assertIs(type(response), dict)
        self.assertIn("articles", response)
        self._test_groups(response["articles"], params["groupby_options"])

    def _test_groups(self, groups, groupby_options):
        group_names = list(
            map(itemgetter("name"), groupby_options["groups"])
        )
        group_names += [groupby_options["default"]]
        for name, articles in groups.items():
            self.assertIn(name, group_names)
            self.assertLessEqual(len(articles), groupby_options["max_results_per_group"])
            self._test_article_format(articles)
            scores = list(map(itemgetter("relevance"), articles))
            diffs = [scores[i] - scores[i-1] for i in range(1, len(scores))]
            self.assertTrue(all(diff <= 0 for diff in diffs))

    def _test_article_format(self, articles):
        self.assertIs(type(articles), list)
        for article in articles:
            self.assertIsInstance(article, dict)
            expected = (
                "title", "body", "language", "relevance", 
                "image_url", "url", 
                "source", "category"
            )
            self.assertTrue(all(key in article for key in expected))
            logger.debug(article["title"])

    def _test_analyse(self, response):
        self.assertIs(type(response), dict)
        self.assertIn('articles', response)
        self.assertIn('graph', response)

    def _make_request(self, params):
        resp = requests.post(self.ENDPOINT, json=params)
        try:
            return resp.json()
        except Exception as err:
            logger.exception(err)
            logger.debug(resp.text)
            raise err


if __name__ == '__main__':
    unittest.main()
