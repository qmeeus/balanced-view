import json
import requests

from tests.utils import debug, load_rss_sources

API_LOCATION = "http://localhost:32597"

def post(url):
    def _post(params):
        return requests.post(url, json=params).json()
    return _post

def test_balancedview():

    from tests.integration_tests.test_balancedview import _test_balancedview
    _test_balancedview(post(API_LOCATION))


def test_rss():
    url = API_LOCATION + "/update"

    sources = load_rss_sources()
    resp = post(url)(sources)        
    
    print(resp)


if __name__ == '__main__':
    test_balancedview()
    test_rss()
