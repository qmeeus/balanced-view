#!/usr/bin/env python3

import os
from collections import OrderedDict
from elasticsearch import Elasticsearch
from typing import Dict, Any

from data_provider.clients.rss_spider import RssFetcher
from data_provider.clients.newsapi import NewsAPIClient
from data_provider.logger import logger 

Json = Dict[str,Any]
INDEX_NAME = "article-index"

def save_resource(resource:Json, counts:Dict[str,int]):
    result = es.index(index=INDEX_NAME, doc_type="article", body=resource)
    for key, value in result["_shard"]:
        counts[key] += value
    return counts

logger.info("Start fetching more data")

es = Elasticsearch([{'host': os.environ["ES_HOST"],'port': os.environ["ES_PORT"]}])
es.indices.create(index=INDEX_NAME, ignore=400)

collection = RssFetcher.from_file()
logger.info(f"Fetch RSS feeds from {len(collection)} sources")

rss_results = OrderedDict({'total': 0, 'successful': 0, 'failed': 0})
for i, article in enumerate(collection.fetch_all()):
    rss_results = save_resource(article, rss_results)

logger.info(f"Added {rss_results['successful']} resources, {rss_results['failed']} errors")

newsapi = NewsAPIClient()
logger.info(f"Getting articles from {len(newsapi.DEFAULT_SOURCES)} sources")

api_results = OrderedDict({'total': 0, 'successful': 0, 'failed': 0})
for article in newsapi.get_top_headlines()["articles"]:
    api_results = save_resource(article, api_results)

all_results = {k: v1 + v2 for (k, v1), (_, v2) in zip(rss_results.items(), api_results.items())}
logger.info(f"Added {api_results['successful']} resources, {api_results['failed']} errors")
logger.info(f"Total added: {all_results['successful']}, total errors: {all_results['failed']}")
