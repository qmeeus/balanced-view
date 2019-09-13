import os.path as p
import datetime as dt
from newsapi import NewsApiClient
from typing import List, Dict, Any, Optional
from api.utils.logger import logger

Json = Dict[str, Any]


class NewsClient(NewsApiClient):

    KEYFILE = "resources/news_apikey"
    DEFAULT_LOOKBACK_IN_DAYS = 30

    def __init__(self, keywords:List[str], sources:List[str], 
                 start_date:Optional[dt.date]=None, end_date:Optional[dt.date]=None, 
                 language:Optional[str]=None) -> None:

        self.keywords = keywords
        self.sources = sources
        self.end_date = end_date or dt.date.today()
        self.start_date = start_date or (self.end_date - dt.timedelta(days=-self.DEFAULT_LOOKBACK_IN_DAYS))
        self.language = language

        full_path = p.join(p.dirname(__file__), self.KEYFILE)
        if not p.exists(full_path):
            raise FileNotFoundError("Please provide the API key")
        with open(full_path) as keyfile:
            super(NewsClient, self).__init__(keyfile.read().strip())

    def fetch_all(self) -> Json:
        logger.info(f"Requesting NewsAPI for {self.keywords}")
        return self.get_everything(
                q=" ".join(self.keywords),
                sources=",".join(self.sources),
                from_param=self.format_date(self.start_date),
                to=self.format_date(self.end_date),
                language=self.language,
                sort_by='relevancy')

    @staticmethod
    def format_date(date:dt.date) -> str:
        return date.strftime('%Y-%m-%d')
