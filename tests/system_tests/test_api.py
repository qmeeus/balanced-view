import json
import requests

from tests.utils import debug, load_rss_sources, load_texts

API_LOCATION = "http://localhost:32597"

def post(url):
    print(f"Starting api test @ {url} endpoint")
    def _post(**params):
        r = requests.post(url, json=params)
        try:
            return r.json()
        except:
            return r.text
    return _post

def test_articles():
    from tests.integration_tests.test_articles import _test_articles
    url = API_LOCATION + "/articles"
    _test_articles(post(API_LOCATION))


def test_analyse():
    url = API_LOCATION + "/analyse"
    for _, text in load_texts():
        resp = post(url)(**{"text": text, "related": True})
        import ipdb; ipdb.set_trace()
        print(resp.keys())


if __name__ == '__main__':
    # test_articles()
    test_analyse()
