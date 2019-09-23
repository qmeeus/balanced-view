import os.path as p
import datetime as dt
from newsapi import NewsApiClient
from typing import List, Dict, Any, Optional, Callable
from api.utils.logger import logger

Json = Dict[str, Any]


class NewsAPIClient(NewsApiClient):

    KEYFILE = "resources/news_apikey"
    DEFAULT_LOOKBACK_IN_DAYS = 30
    DEFAULT_SOURCES = [
        "the-guardian-uk",
        "independent",
        "msnbc",
        "politico",
        "reuters",
        "financial-times",
        "bbc-news",
        "the-wall-street-journal",
        "cnn",
        "bloomberg",
        "daily-mail",
        "fox-news", 
        "the-telegraph",
    ]

    class Parser:

        def __init__(self, decorated:Callable):
            self._decorated = decorated

        def __call__(self, *args:Any, **kwargs:Any):
            logger.debug(f"func.__name__: {args}, {kwargs}")
            response = self._decorated(*args, **kwargs)
            logger.debug(f"Status: {response['status']}, Total results: {response['totalResults']}")
            return response["articles"]

    def __init__(self, sources:Optional[List[str]]=None, 
                 start_date:Optional[dt.date]=None, end_date:Optional[dt.date]=None, 
                 language:Optional[str]=None) -> None:

        self.sources = sources or self.DEFAULT_SOURCES
        self.end_date = end_date or dt.date.today()
        self.start_date = start_date or (self.end_date - dt.timedelta(days=-self.DEFAULT_LOOKBACK_IN_DAYS))
        self.language = language

        full_path = p.join(p.dirname(__file__), self.KEYFILE)
        if not p.exists(full_path):
            raise FileNotFoundError("Please provide the API key")
        with open(full_path) as keyfile:
            super(NewsAPIClient, self).__init__(keyfile.read().strip())

    @Parser
    def get_everything(self, keywords:List[str]) -> Json:
        return super(NewsAPIClient, self).get_everything(
            q=" ".join(keywords),
            sources=",".join(self.sources),
            from_param=self.format_date(self.start_date),
            to=self.format_date(self.end_date),
            language=self.language,
            sort_by='relevancy')

    @Parser
    def get_top_headlines(self, query:Optional[str]=None, 
                          country:Optional[str]=None, 
                          category:Optional[str]=None) -> Json:

        return super(NewsAPIClient, self).get_top_headlines(
            q=query,
            sources=self.sources, 
            language=self.language, 
            country=country, 
            category=category
        )

    @staticmethod
    def format_date(date:dt.date) -> str:
        return date.strftime('%Y-%m-%d')
