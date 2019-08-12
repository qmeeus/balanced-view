import os.path as p
from newsapi import NewsApiClient


class NewsClient(NewsApiClient):

    keyfile = "news_apikey"

    def __init__(self):
        full_path = p.join(p.dirname(__file__), self.keyfile)
        if not p.exists(full_path):
            raise FileNotFoundError("Please provide the API key")
        with open(full_path) as keyfile:
            super(NewsClient, self).__init__(keyfile.read().strip())

