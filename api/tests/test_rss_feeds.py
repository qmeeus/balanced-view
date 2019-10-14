import unittest
import os.path as p
import datetime as dt
from operator import itemgetter, attrgetter
import json
from time import time

from api.data_provider.sources.rss_spider import RssFeed, RssFetcher
from tests.utils import load_rss_sources
from api.utils.logger import logger


class Meta(unittest.TestCase):

    def _test_article(self, article):
        self.assertIs(type(article), dict)
        expected = [
            ("source", dict), ("category", str), 
            ("title", str), ("body", str), 
            ("publication_date", dt.datetime)
        ]
        for key, typ in expected:
            self.assertIn(key, article)
            self.assertIs(type(article[key]), typ)

        logger.debug(article["title"])
        logger.debug(article["body"])

class TestRssFeed(Meta):

    def __init__(self, *args, **kwargs):
        self._source_dict = load_rss_sources()["sources"][0]
        super(TestRssFeed, self).__init__(*args, **kwargs)

    def test_constructor_from_dict(self):
        feed = RssFeed.from_dict(self._source_dict)
        expected_attr = [
            ("name", str), ("id", str), 
            ("url", str), ("categories", list),
            ("country", str), ("language", str)
        ]
        for attr, typ in expected_attr:
            self.assertTrue(hasattr(feed, attr))
            self.assertIsInstance(getattr(feed, attr), typ)

        self.assertTrue(all(type(c) is dict for c in feed))
        self.assertIs(type(feed.available_categories), list)

    def test_fetch_articles(self):
        feed = RssFeed.from_dict(self._source_dict)
        for result in feed.get_latest(["Headlines"]):
            self._test_article(result)


class TestRssFetcher(Meta):

    def __init__(self, *args, **kwargs):
        self._source_dict = load_rss_sources()
        super().__init__(*args, **kwargs)

    def test_constructor_from_file(self):
        collection = RssFetcher.from_file()
        self._test_init(collection)

    def test_filter(self):
        collection = RssFetcher.from_file()
        filters = {"lang": "nl", "country": "be"}
        sources = collection.find_all(**filters)
        self._test_not_empty(sources)

        filters = dict(id=["vrt", "standaard"], **filters)
        sources = collection.find_all(**filters)
        self._test_not_empty(sources)

        categories = ["Headlines", "Latest", "Buitenland"]
        sources = collection.find_all(categories=categories)
        self._test_not_empty(sources)
        assert all(
            all(
                c in categories for c in s.available_categories
            ) for s in sources
        )

        filters = dict(categories=categories, **filters)
        sources = collection.find_all(**filters)
        self._test_not_empty(sources)

    def test_fetch_articles(self):
        start = time()
        collection = RssFetcher.from_file()
        for result in collection.fetch_all():
            self._test_article(result)
        logger.debug(f"Job took {time() - start}")

    def _test_not_empty(self, sources):   
        self.assertTrue(all(isinstance(s, RssFeed) for s in sources))
        self.assertNotEqual(len(sources), 0)

    def _test_init(self, collection):
        self.assertIsInstance(collection, RssFetcher)
        self.assertTrue(all(isinstance(s, RssFeed) for s in collection))
        cats = collection.available_sources
        self.assertIs(type(cats), list)
        self.assertTrue(all(type(cat) is str for cat in cats))
        self.assertTrue(all(
            isinstance(collection[cat], RssFeed) for cat in cats
        ))




if __name__ == "__main__":
    unittest.main()
