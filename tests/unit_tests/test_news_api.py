from datetime import date
import types

from tests.utils import safe, debug
from api.data_provider.sources.newsapi import NewsAPIClient


def test_news_api():
    # keywords = "trump republican shootings el paso".split()
    # sources = "cnn,fox-news,politico".split(",")
    newsapi = NewsAPIClient()
    articles = newsapi.get_top_headlines()
    assert articles and isinstance(articles, types.GeneratorType)

    expected_keys = ("title", "body", "publication_date", "source", "language", "category")

    for article in articles:
        assert type(article) is dict
        for key in expected_keys:
            assert key in article, f"Missing {key}"
            if not article[key]: 
                print(f"Empty {key}")

        print("Title:", article["title"], "Published:", article["publication_date"], "Language:", article["language"])
        print("Source:", article["source"]["name"], "Category:", article["category"])



if __name__ == "__main__":
    import ipdb; ipdb.set_trace()
    test_news_api()
