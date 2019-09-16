from tests.unit_tests.test_ibm_api import test_ibm_translate
from tests.unit_tests.test_summa_api import test_summa
from tests.unit_tests.test_news_api import test_news_api

__all__ = [
    "test_ibm_translate",
    "test_summa",
    "test_news_api",
]


def main():
    test_ibm_translate()
    test_summa()
    test_news_api()

