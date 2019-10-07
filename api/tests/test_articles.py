import unittest
import os
import requests
from operator import itemgetter
from api.utils.exceptions import BackendError
from api.tests.utils import load_keywords
from api.engine.articles import fetch_articles
from api.utils.logger import logger

class TestArticles(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        url = "http://{ES_HOST}:{ES_PORT}".format(**os.environ)
        r = requests.get(url)
        super(TestArticles, self).__init__(*args, **kwargs)

    def test_fails_on_string_query(self):
        lang, keywords = "en", "Trump,Ukraine,Elections"
        params = {"terms": keywords, "source_language": lang}
        with self.assertRaises(BackendError):
            fetch_articles(**params)

    def test_fails_on_string_languages(self):
        lang, keywords = "en", ["Trump","Ukraine","Elections"]
        params = {"terms": keywords, "source_language": lang, "search_languages": "fr,nl,en"}
        with self.assertRaises(BackendError):
            fetch_articles(**params)

    def test_fetch_articles_basic(self):
        for lang, keywords in load_keywords():
            query = keywords.split(",")
            params = {
                "terms": query, 
                "source_language": lang, 
                "search_languages": ["fr","nl","en"]
            }
            response = self._test_response(params)
            self._test_article_format(response["articles"])

    def test_fetch_articles_groups(self):
        groupby_options = {
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
        for lang, keywords in load_keywords():
            query = keywords.split(",")
            params = {
                "terms": query, 
                "source_language": lang, 
                "search_languages": ["fr","nl","en"],
                "groupby_options": groupby_options
            }
            response = self._test_response(params)
            groups = list(map(itemgetter("name"), groupby_options["groups"]))
            groups += [groupby_options["default"]]
            for name, articles in response["articles"].items():
                self.assertIn(name, groups)
                self.assertLessEqual(len(articles), groupby_options["max_results_per_group"])
                self._test_article_format(articles)
                scores = list(map(itemgetter("relevance"), articles))
                diffs = [scores[i] - scores[i-1] for i in range(1, len(scores))]
                self.assertTrue(all(diff <= 0 for diff in diffs))

    def _test_response(self, params):
        response = fetch_articles(**params)
        self.assertIs(type(response), dict)
        self.assertIn("articles", response)
        return response

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


if __name__ == '__main__':
    unittest.main()