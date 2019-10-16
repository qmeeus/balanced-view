import os, os.path as p
import json
import re
from operator import itemgetter, attrgetter
from urllib.parse import urljoin
from copy import deepcopy
import requests
import feedparser
from datetime import datetime as dt
from time import mktime
from threading import Thread, Lock
from queue import Queue
from typing import Iterator, List, Dict, Union, Optional, Iterable, Tuple, Any

from api.utils.logger import logger


Json = Dict[str,Any]
Category = Dict[str,str]
Categories = List[Category]
ResultIterator = Iterator[Json]


class RssFeed:

    """
    RssFeed of RSS feed containing multiple categories corresponding
    to urls.
    self.get_latest is a generator that takes a list of categories (default=all)
    and yields the feeds for each category using feedparser library
    """

    N_THREADS = 12
    
    def __init__(self, name:str, 
                 id:str, 
                 url:str, 
                 country:str, 
                 lang:str, 
                 categories:List[Dict[str, str]]) -> None:

        self.name = name
        self.id = id
        self.url = url
        self.country = country
        self.language = lang
        self.categories = categories

        self._results = {}

    def __repr__(self) -> str:
        return f"RssFeed({self.name})"

    def __iter__(self) -> Iterable[Category]:
        return self.categories.__iter__()

    def __getitem__(self, category_name:str) -> Category:
        for category in self.categories:
            if category["name"] == category_name:
                return category
        raise KeyError(category_name)

    def __contains__(self, category_name:str) -> bool:
        return bool(self[category_name])

    @property
    def available_categories(self) -> List[str]:
        return list(map(itemgetter("name"), self.categories))

    def update_categories(self, selection:Categories) -> Categories:
        f = lambda x: x["name"] in selection
        self.categories = list(filter(f, self.categories))
        return self.categories

    def get_category(self, category_name:str) -> Category:
        logger.warn(DeprecationWarning("Replace self.get_category(name) to self[name]"))
        for category in self.categories:
            if category["name"] == category_name:
                return category
        raise KeyError(category_name)

    def get_url(self, category_name:str) -> str:
        avail = self.available_categories
        if category_name not in avail:
            raise KeyError(category_name)
        filter_func = lambda el: el["name"] == category_name
        selected = list(filter(filter_func, self.categories))
        if len(selected) > 1:
            logger.warn(f"More than one categories with name {category_name}")
        return urljoin(self.url, selected[0]["url"])

    def get_latest(self, categories:Optional[List[str]]=None) -> ResultIterator:
        categories = categories or self.available_categories
        queue = Queue()

        def threader() -> None:
            while True:
                category = queue.get()
                self.get_category_feed(category)
                queue.task_done()

        for _ in range(self.N_THREADS):
            thread = Thread(target=threader)
            thread.daemon = True
            thread.start()

        for category in categories:
            queue.put(category)

        queue.join()
        yield from self._parse_results()

    def get_category_feed(self, category_name:str) -> None:
        if category_name not in self.available_categories:
            return
        url = self.get_url(category_name)
        logger.info(f"Request feed from {url}")
        result = feedparser.parse(url)
        if hasattr(result, "status"):
            if result.status // 400 > 0:
                raise requests.HTTPError(result.status)
        else:
            logger.warn(result)
        
        with Lock():
            self._results[category_name] = result

    def _parse_results(self) -> ResultIterator:
        for category, result in self._results.items():
            for entry in result.entries:
                yield self.parse_entry(entry, category)

    def to_dict(self) -> Dict[str,str]:
        return dict(
            name=self.name, 
            id=self.id, 
            url=self.url, 
            language=self.language)

    @classmethod
    def from_dict(cls, attributes:Json) -> 'RssFeed':
        return cls(**attributes)

    def parse_entry(self, entry:Json, category:str) -> Json:
        """
        Parse the entries gotten from feedparser to the format expected by elasticsearch
        See models.py for information about the expected schema
        The category is required since it is not included in the entry
        """
        parsed = {}
        parsed["title"] = self.clean_text(entry["title"])
        parsed["body"] = self.clean_text(entry["summary"])
        parsed["publication_date"] = dt.fromtimestamp(mktime(entry["published_parsed"]))
        parsed["language"], parsed["country"] = self.parse_locale(entry)
        parsed["source"] = self.to_dict()
        parsed["category"] = category
        parsed["url"] = entry["link"]
        parsed["image_url"] = self.parse_image_url(entry)
        return parsed

    def parse_locale(self, entry:Json) -> Tuple[str, str]:
        lang, country = self.language, self.country
        lang = entry["title_detail"].pop("language", None) or lang
        if "-" in lang:
            lang, country = lang.split("-")
        return lang, country

    @staticmethod
    def parse_image_url(entry:Json) -> str:
        f_img = lambda link: link["type"].startswith("image")
        urls = list(map(itemgetter("href"), filter(f_img, entry.get("links", []))))
        if urls:
            return urls[0]
        img_tag = re.search(r"<img\s+src\=[\"\'](http.*?)[\"\']\s*(?:.*?)?\/>", entry["summary"])
        if img_tag:
            return img_tag.group(1)
        return ""

    @staticmethod
    def clean_text(text:str) -> str:
        # Remove html tags
        text = re.sub('<.*?>', '', text)
        return text


class RssFetcher:

    """
    Collection of RSS sources containing sources to RSS feeds.
    RssFetcher  is initialised from a list of sources definitions. 
    The helper methods from_dict and from_file are available to load 
    directly the sources from multiple origin (for example generated 
    with json.load or stored in a json file).
    The method self.fetch_all takes filters as keyword arguments that
    correspond to attributes of the sources and returns a generator of
    RSS feeds for the filtered sources.
    """

    SOURCE_FILE = "resources/rss_sources.json"

    def __init__(self, sources:List[dict]) -> None:
        self.sources = self.convert_sources(sources)
        
    def __repr__(self) -> str:
        return f"RssFetcher({p.basename(self.SOURCE_FILE)})"

    def __iter__(self) -> Iterable[RssFeed]:
        return self.sources.__iter__()

    def __getitem__(self, source_id:str) -> RssFeed:
        return self.get_source(id=source_id)

    def __contains__(self, source_id:str) -> bool:
        return bool(self[source_id])

    def get_source(self, **identifiers:Union[str,List[str]]) -> RssFeed:
        source = self.find_all(**identifiers)
        if len(source) > 1:
            logger.warn(f"Parameters {identifiers} not unique")
        elif len(source) < 1:
            logger.error(f"No source found with parameters {identifiers}")
            raise KeyError(identifiers)
        return source[0]

    @property
    def available_sources(self) -> List[str]:
        return list(map(attrgetter("id"), self.sources))

    def fetch_all(self, **filters:Union[str,List[str]]) -> ResultIterator:
        sources = self.find_all(**filters)
        for source in sources:
            yield from source.get_latest()

    def find_all(self, categories:Optional[List[str]]=None, **filters:Union[str,List[str]]) -> List[RssFeed]:
        """Returns a copy of the sources that match the provided filters, each containing
        only the given categories. The output is only calculated in the return statement.
        Params:
            categories: list of category names to match against each source categories
            filters: key, value mapping where key is an attribute of RssFeed and value can 
            be one or more strings to include in the output

        Returns: the list of filtered sources that match the provided filters with the provided categories
        """
        sources = iter(deepcopy(self.sources))
        if categories:
            f = lambda s: s.update_categories(categories)
            sources = filter(f, sources)

        for key, value in filters.items():

            if isinstance(value, (list, tuple, set)):
                func = lambda element: getattr(element, key) in value
            else:
                func = lambda element: getattr(element, key) == value

            sources = filter(func, sources)
        
        return list(sources)

    @classmethod
    def from_dict(cls, sources_dict:Json) -> 'RssFetcher':
        return cls(sources_dict["sources"])

    @classmethod
    def from_file(cls, filename:Optional[str]=None) -> 'RssFetcher':
        filename = filename or cls.SOURCE_FILE
        full_path = p.abspath(p.join(p.dirname(__file__), filename))
        with open(full_path) as json_file:
            return cls.from_dict(json.load(json_file))

    @staticmethod
    def convert_sources(sources:List[Json]) -> List[RssFeed]:
        return list(map(RssFeed.from_dict, sources))

