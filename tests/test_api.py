import requests
from tests.test_balancedview import _test_balancedview

API_LOCATION = "http://localhost:9999"
# API_LOCATION = "http://cardia.cs.kuleuven.be:8080/api"

def test_api():
    
    def api_request(params):
        return requests.post(API_LOCATION, data=params).json()

    _test_balancedview(api_request)


if __name__ == '__main__':
    test_api()