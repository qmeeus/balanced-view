from pprint import pprint
from tests.utils import load_test_data

def _test_balancedview(func):
    for text in load_test_data():
        params = {"text": text}
        response = func(params)
        print("Graph:")
        if "error" in response["graph"]:
            print(response["graph"]["error"]["text"])
        else:
            print("{} nodes, {} edges".format(len(response["graph"]["nodes"]), len(response["graph"]["links"])))
        print("Articles:")
        if "error" in response["articles"]:
            print("Error with text:")
            print(text[:80], "(...)")
            print(response["articles"]["error"]["text"], response["articles"]["error"]["reason"])
        else:
            print("; ".join([
                "{}: {}".format(orientation, str(len(articles))) for orientation, articles in response["articles"].items()]))

def test_balancedview():
    from api.engine.articles import fetch_articles
    _test_balancedview(fetch_articles)


if __name__ == '__main__':
    test_balancedview()