import requests
import warnings
from bs4 import BeautifulSoup
from tests.utils import load_test_data

# UI_LOCATION = "http://localhost:8080"
UI_LOCATION = "http://cardia.cs.kuleuven.be:8080"


def _test_post_request(text, csrf_token):
    params = {"text": text, "csrf_token": csrf_token}
    resp = requests.post(UI_LOCATION, params)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    graph_container = soup.find("div", {"id": "graph-container"})
    if not graph_container:
        warnings.warn("No graph found")
    articles = soup.find_all("div", {"class": "thumbnail article"})
    print(f"{len(articles)} articles", end=" ")

def test_ui():

    resp = requests.get(UI_LOCATION)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    csrf_token = soup.find("input", {"id": "csrf_token"}).get("value")
    assert bool(csrf_token)

    for i, text in enumerate(load_test_data()):
        title = text.strip().split('\n')[0]
        print(f"Text #{i}: {title[:50]}...", end=" ")
        _test_post_request(text, csrf_token)
        print("Done")

if __name__ == "__main__":
    test_ui()