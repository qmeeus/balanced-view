from datetime import date
import types
import unittest

from api.data_provider.sources.newsapi import NewsAPIClient
from api.utils.logger import logger


class TestNewsAPI(unittest.TestCase):

    def test_newsapi(self):
        newsapi = NewsAPIClient()
        articles = newsapi.get_top_headlines()
        self.assertTrue(bool(articles))
        self.assertIsInstance(articles, types.GeneratorType)

        expected_keys = ("title", "body", "publication_date", "source", "language", "category")

        for article in articles:
            assert type(article) is dict
            for key in expected_keys:
                self.assertIn(key, article)
                if not article[key]: 
                    logger.debug(f"Empty {key}")

            logger.debug(
                "Title: {title} Published: {publication_date} Language: {language}"
                .format(**article)
            )
            logger.debug(f"Source: {article['source']['name']} Category: {article['category']}")


if __name__ == "__main__":
    unittest.main()
