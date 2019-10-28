import os.path as p
import datetime as dt
from dateutil.parser import parse as dateparse
from newsapi import NewsApiClient
import json
from typing import List, Dict, Any, Optional, Callable, Iterator
from api.utils.logger import logger

Json = Dict[str, Any]
Results = Iterator[Json]

def abspath(relpath):
    return p.abspath(p.join(p.dirname(__file__), relpath))


class NewsAPIClient(NewsApiClient):

    KEYFILE = "../../resources/news_apikey"
    DEFAULT_LOOKBACK_IN_DAYS = 30
    SOURCEFILE = "resources/api_sources.json"
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

    def __init__(self, start_date:Optional[dt.date]=None, 
                 end_date:Optional[dt.date]=None, 
                 language:Optional[str]=None) -> None:

        self.available_sources = self.load_sources()
        self.end_date = end_date or dt.date.today()
        self.start_date = start_date or (self.end_date - dt.timedelta(days=-self.DEFAULT_LOOKBACK_IN_DAYS))
        self.language = language

        full_path = abspath(self.KEYFILE)
        if not p.exists(full_path):
            raise FileNotFoundError("Please provide the API key")
        with open(full_path) as keyfile:
            super(NewsAPIClient, self).__init__(keyfile.read().strip())

    def pager(self, method:Callable, page_size:Optional[int]=100, **kwargs:Any) -> Results:
        logger.debug(f"{method.__name__}: {kwargs}")

        n_articles = 0
        total_results = 1
        while n_articles < total_results:
            kwargs["page_size"] = page_size
            kwargs["page"] = n_articles // page_size + 1
            response = method(**kwargs)
            total_results = response["totalResults"]
            if not n_articles:
                logger.debug(f"{total_results} results")
            cat, lang = kwargs.get("category", ""), kwargs.get("language", "")
            yield from map(self.parse(cat, lang), response["articles"])
            n_articles += page_size
            break  # Developer accounts are limited to a max of 100 results.

    def get_everything(self, keywords:List[str], 
                       sources:Optional[List[str]]=None, 
                       language:Optional[str]=None,
                       start_date:Optional[dt.date]=None,
                       end_date:Optional[dt.date]=None,
        ) -> Results:

        options = {
            'q': " ".join(keywords),
            'sources': ",".join(sources or self.DEFAULT_SOURCES),
            'from_param': self.format_date(start_date or self.start_date),
            'to': self.format_date(end_date or self.end_date),
            'language': language,
            'sort_by': 'relevancy'
        }

        yield from self.pager(super(NewsAPIClient, self).get_everything, **options)

    def get_top_headlines(self, query:Optional[str]=None, 
                          sources:Optional[List[str]]=None,
                          country:Optional[str]=None, 
                          category:Optional[str]=None) -> Results:

        options = {
            'q': query,
            'sources': ",".join(sources or self.DEFAULT_SOURCES),
            'country': country, 
            'category': category
        }

        yield from self.pager(super(NewsAPIClient, self).get_top_headlines, **options)

    def load_sources(self) -> Json:
        with open(abspath(self.SOURCEFILE)) as f:
            sources = json.load(f)["sources"]
        return {source["id"]: source for source in sources}

    def parse(self, category:str, language:str) -> Callable:
        def _parse(article:Json) -> Json:
            parsed = {}
            parsed["title"] = article["title"]
            parsed["body"] = article["description"]
            parsed["publication_date"] = dateparse(article["publishedAt"])
            parsed["source"] = self.available_sources[article["source"]["id"]]
            parsed["language"] = language or parsed["source"]["language"]
            parsed["category"] = category or parsed["source"]["category"]
            parsed["url"] = article["url"]
            parsed["image_url"] = article["urlToImage"]
            return parsed
        return _parse

    @staticmethod
    def format_date(date:dt.date) -> str:
        return date.strftime('%Y-%m-%d')
