# from pprint import pprint
from tests.utils import load_keywords

def _test_articles(func):
    for lang, keywords in load_keywords():
        # import ipdb; ipdb.set_trace()
        params = {"terms": keywords, "source_language": lang, "search_languages": "fr,nl,en"}
        response = func(**params)
        import ipdb; ipdb.set_trace()
        assert type(response) is dict
        assert "articles" in response
        # import ipdb; ipdb.set_trace()
        for article in response["articles"]:
            assert type(article) is dict
            expected = ("category", "body", "title", "language", "image_url", "url", "source")
            assert all(key in article for key in expected)
            print(article["title"])

        # print("Graph:")
        # if "error" in response["graph"]:
        #     print(response["graph"]["error"]["text"])
        # else:
        #     print("{} nodes, {} edges".format(len(response["graph"]["nodes"]), len(response["graph"]["links"])))
        # print("Articles:")
        # if "error" in response["articles"]:
        #     print("Error with text:")
        #     print(text[:80], "(...)")
        #     print(response["articles"]["error"]["text"], response["articles"]["error"]["reason"])
        # else:
        #     print("; ".join([
        #         "{}: {}".format(orientation, str(len(articles))) for orientation, articles in response["articles"].items()]))


def test_articles():
    from api.engine.articles import fetch_articles
    _test_articles(fetch_articles)


if __name__ == '__main__':
    test_articles()
