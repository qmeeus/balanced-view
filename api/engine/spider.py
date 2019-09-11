import os, os.path as p
import json
from operator import itemgetter, attrgetter
from urllib.parse import urljoin
from copy import deepcopy
import requests
import feedparser

from api.utils.logger import logger
from api.utils.functools import member, member, member_item


class Source:
    
    def __init__(self, name, id, url, country, lang, categories):
        self.name = name
        self.id = id
        self.url = url
        self.country = country
        self.lang = lang
        self.categories = categories

    def __repr__(self):
        return f"Source({self.name})"

    def __iter__(self):
        return self.categories.__iter__()

    def __contains__(self, category):
        return category in map(itemgetter("name"), self.categories)

    @property
    def available_categories(self):
        return list(map(itemgetter("name"), self.categories))

    def update_categories(self, selection):
        f = member_item(selection, "name")
        self.categories = list(filter(f, self.categories))
        return self.categories

    def get_category(self, name):
        for category in self.categories:
            if category["name"] == name:
                return category

    def get_url(self, category):
        avail = self.available_categories
        if category not in avail:
            raise KeyError(category)
        filter_func = lambda el: el["name"] == category
        selected = list(filter(filter_func, self.categories))
        if len(selected) > 1:
            logger.warn(f"More than one categories with name {category}")
        return urljoin(self.url, selected[0]["url"])

    def get_latest(self, categories=None):
        categories = categories or self.available_categories
        for category in categories:
            if category not in self.available_categories:
                continue
            url = self.get_url(category)
            logger.info(f"Request feed from {url}")
            result = feedparser.parse(url)
            if result.status // 400 > 0:
                raise requests.HTTPError(result.status)
            yield self.id, category, result.entries

    def to_dict(self):
        return dict(
            name=self.name, 
            id=self.id, 
            url=self.url, 
            lang=self.lang)

    @classmethod
    def from_dict(cls, attributes):
        return cls(**attributes)

class SourceCollection:

    SOURCE_FILE = "resources/rss_sources.json"

    def __init__(self, sources):
        self.sources = self.convert_sources(sources)
        
    def __repr__(self):
        return f"SourceCollection({p.basename(self.SOURCE_FILE)})"

    def __iter__(self):
        return self.sources.__iter__()

    def __getitem__(self, source_id):
        return self.get_source(id=source_id)

    def __contains__(self, source_id):
        return source_id in map(attrgetter("id"), self.sources)

    def get_source(self, **identifiers):
        source = self.find_all(**identifiers)
        if len(source) > 1:
            logger.warn(f"Parameters {identifiers} not unique")
        elif len(source) < 1:
            logger.error(f"No source found with parameters {identifiers}")
            raise KeyError(identifiers)
        return source[0]


    @property
    def available_sources(self):
        return list(map(attrgetter("id"), self.sources))

    def fetch_all(self, **filters):
        sources = self.find_all(**filters)
        for source in sources:
            yield from source.get_latest()

    def find_all(self, **filters):
        sources = deepcopy(self.sources)
        categories = filters.pop("categories", None)
        if categories:
            f = lambda s: s.update_categories(categories)
            sources = filter(f, sources)

        for key, value in filters.items():
            if isinstance(value, (list, tuple, set)):
                func = lambda el: getattr(el, key) in value
            elif value is None:
                func = lambda _: True
            else:
                func = lambda el: getattr(el, key) == value
            sources = filter(func, sources)
        
        return list(sources)

    @classmethod
    def from_dict(cls, sources_dict):
        return cls(sources_dict["sources"])

    @classmethod
    def from_file(cls, filename=None):
        filename = filename or cls.SOURCE_FILE
        full_path = p.abspath(p.join(p.dirname(__file__), filename))
        with open(full_path) as json_file:
            return cls.from_dict(json.load(json_file))

    @staticmethod
    def convert_sources(sources):
        return list(map(Source.from_dict, sources))

