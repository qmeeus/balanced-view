import unittest
from api.tests.test_ibm_api import TestIBMAPI
from api.tests.test_news_api import TestNewsAPI
from api.tests.test_rss_feeds import TestRssFeed, TestRssFetcher
from api.tests.test_data_provider import TestDataProvider
from api.tests.test_text import TestTextAnalyser
from api.tests.test_articles import TestArticles
from api.tests.test_ui import TestUI
from api.tests.test_server import TestServer

def make_suite(*TestCases):
    suite = unittest.TestSuite()
    for TextCase in TestCases:
        tests = unittest.TestLoader().loadTestsFromTestCase(TextCase)
        suite.addTests(tests)
    return suite

def test_api():
    return make_suite(TestIBMAPI, TestArticles, TestTextAnalyser)
    

def test_data_provider():
    return make_suite(TestNewsAPI, TestRssFeed, TestRssFetcher, TestDataProvider)

def test_ui():
    return make_suite(TestUI)

def test_server():
    return make_suite(TestServer)



def all_tests():
    suite = unittest.TestSuite()
    suite.addTests(test_api())
    suite.addTests(test_data_provider())
    suite.addTests(test_ui())
    suite.addTests(test_server())
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(all_tests())
