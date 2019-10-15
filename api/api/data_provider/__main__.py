#!/usr/bin/env python3

import os
from hashlib import md5
from collections import OrderedDict
from typing import Dict, Any

from api.data_provider.models import Article
from api.data_provider.sources.rss_spider import RssFetcher
from api.data_provider.sources.newsapi import NewsAPIClient
from api.utils.logger import logger 

Json = Dict[str,Any]


def save_resource(resource:Json, counts:Dict[str,int]) -> Dict[str,int]:
    try:
        if not resource["body"]:
            raise ValueError("Empty body")
        article_id = md5(resource["body"].encode()).hexdigest()
        article = Article(meta={"id": article_id}, **resource)
        article.save()
        counts["successful"] += 1

    except Exception as err:
        logger.error(err)
        counts["failed"] += 1

    counts["total"] += 1
    return counts

def fetch_rss() -> Dict[str,int]:

    collection = RssFetcher.from_file()
    logger.info(f"Fetch RSS feeds from {len(collection.sources)} sources")

    rss_results = OrderedDict({'total': 0, 'successful': 0, 'failed': 0})
    for article in collection.fetch_all():
        rss_results = save_resource(article, rss_results)

    logger.info(f"Added {rss_results['successful']} resources, {rss_results['failed']} errors")
    return rss_results

def fetch_newsapi() -> Dict[str,int]:
    newsapi = NewsAPIClient()
    logger.info(f"Getting articles from {len(newsapi.DEFAULT_SOURCES)} sources")

    api_results = OrderedDict({'total': 0, 'successful': 0, 'failed': 0})
    for article in newsapi.get_top_headlines():
        api_results = save_resource(article, api_results)

    logger.info(f"Added {api_results['successful']} resources, {api_results['failed']} errors")
    return api_results


logger.info("Start fetching more data")
rss_results = fetch_rss()
api_results = fetch_newsapi()
all_results = {k: v1 + v2 for (k, v1), (_, v2) in zip(rss_results.items(), api_results.items())}
logger.info(f"Total added: {all_results['successful']}, total errors: {all_results['failed']}")
