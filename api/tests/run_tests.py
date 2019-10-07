import unittest
from api.tests.test_ibm_api import TestIBMAPI
from api.tests.test_news_api import TestNewsAPI
from api.tests.test_rss_feeds import TestRssFeed, TestRssFetcher
from api.tests.test_text import TestTextAnalyser
from api.tests.test_articles import TestArticles

def make_suite(*TestCases):
    suite = unittest.TestSuite()
    for TextCase in TestCases:
        tests = unittest.TestLoader().loadTestsFromTestCase(TextCase)
        suite.addTests(tests)
    return suite

def test_api():
    return make_suite(TestIBMAPI, TestArticles, TestTextAnalyser)
    

def test_data_provider():
    return make_suite(TestNewsAPI, TestRssFeed, TestRssFetcher)


def all_tests():
    suite = unittest.TestSuite()
    suite.addTests(test_api())
    suite.addTests(test_data_provider())
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(all_tests())
