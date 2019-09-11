import json
import requests

API_LOCATION = "http://localhost:32597"

def post(url):
    def _post(params):
        return requests.post(url, json=params).json()
    return _post


def test_api():

    from tests.test_balancedview import _test_balancedview
    _test_balancedview(post(API_LOCATION))


def test_update():
    url = API_LOCATION + "/update"

    with open("tests/rss_sources.json") as f:
        sources = json.load(f)

    resp = post(url)(sources)        
    
    print(resp)


if __name__ == '__main__':
    test_api()
    # test_update()