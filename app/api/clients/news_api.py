import os.path as p
from newsapi import NewsApiClient


class NewsClient(NewsApiClient):

    keyfile = "api_resources/news_apikey"

    def __init__(self, keywords, sources, start_date, end_date, language):
        full_path = p.join(p.dirname(__file__), self.keyfile)
        self.keywords = keywords
        self.sources = sources
        self.start_date = start_date
        self.end_date = end_date
        self.language = language

        if not p.exists(full_path):
            raise FileNotFoundError("Please provide the API key")
        with open(full_path) as keyfile:
            super(NewsClient, self).__init__(keyfile.read().strip())

        self.articles = self.get_everything(
                q=self.keywords,
                sources=self.sources,
                from_param=self.start_date,
                to=self.end_date,
                language=self.language,
                sort_by='relevancy')
