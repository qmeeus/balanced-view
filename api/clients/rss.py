import feedparser
import json
import warnings
import operator
from urllib.parse import urljoin
from copy import deepcopy
from api.utils.logger import logger

class RSSFeed:

    def __init__(self, source_file):
        self.sources = self.load_sources(source_file)

    def __getitem__(self, source_id):
        source = self.get(id=source_id)
        if len(source) > 1:
            logger.warn(f"Source id {source_id} is not unique")
        elif len(source) < 1:
            logger.error(f"Source id {source_id} not found")
            raise KeyError(source_id)
        return source[0]

    def get(self, **filters):
        return self._filter(self.sources, **filters)

    def get_all_feeds(self, categories=None):
        return {source_id: self.get_feeds(source_id, categories=categories) 
                for source_id in self._filter(self.sources, return_value="id")}

    def get_feeds(self, source_id, categories=None):
        source = self[source_id]
        results = {}
        for category in self._filter(source["categories"], name=categories):
            url = urljoin(source["url"], category["url"])
            logger.info(f"Request feed from {url}")
            results[category] = feedparser.parse(url)["entries"]
        return results

    @property
    def available_sources(self):
        return self._filter(self.sources, return_value="name")

    @staticmethod
    def _filter(mapping, return_value=None, **filters):
        mapping = deepcopy(mapping)
        for key, value in filters.items():
            if isinstance(value, (list, tuple, set)):
                func = lambda el: el[key] in value
            elif value is None:
                func = lambda _: True
            else:
                func = lambda el: el[key] == value
            mapping = filter(func, mapping)
        if return_value is not None:
            mapping = map(operator.itemgetter(return_value), mapping)
        return list(mapping)

    @staticmethod
    def load_sources(source_file):
        with open(source_file) as json_file:
            return json.load(json_file)["sources"]
