import unittest
import os
import requests
from operator import itemgetter
from api.utils.exceptions import BackendError
from tests.utils import load_keywords
from api.engine.articles import fetch_articles
from api.utils.logger import logger

class Meta:

    def __init__(self, *args, **kwargs):
        url = "http://{ES_HOST}:{ES_PORT}".format(**os.environ)
        r = requests.get(url)
        if r.status_code != 200:
            raise ConnectionError("ElasticSearch not available: {r.text}")

        super(Meta, self).__init__(*args, **kwargs)

    def _make_request(self, params):
        raise NotImplementedError

    def _test_response(self, params):
        response = self._make_request(params)
        self.assertIs(type(response), dict)
        self.assertIn("articles", response)

        if "groupby_options" in params:
            self._test_groups(response["articles"], params["groupby_options"])
        else:
            self._test_article_format(response["articles"])

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
            self._test_response(params)

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
            self._test_response(params)


class TestArticles(unittest.TestCase, Meta):

    def _make_request(self, params):
        return fetch_articles(**params)


if __name__ == '__main__':
    unittest.main()