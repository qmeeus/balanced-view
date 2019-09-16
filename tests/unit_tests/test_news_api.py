from datetime import date

from tests.utils import safe
from api.clients import NewsClient


@safe
def test_news_api():
    keywords = "trump republican shootings el paso".split()
    sources = "cnn,fox-news,politico".split(",")
    newsapi = NewsClient(keywords, sources, language="en")
    articles = newsapi.fetch_all()
    assert articles and type(articles) is dict

    assert articles["status"] == "ok"
    assert articles["totalResults"] > 0

    for article in articles["articles"]:
        print(article["source"]["name"], ":", article["title"])


if __name__ == "__main__":
    import ipdb; ipdb.set_trace()
    test_news_api()
