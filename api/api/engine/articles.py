import os
from collections import OrderedDict
from operator import itemgetter, attrgetter
from elasticsearch_dsl import Search, MultiSearch, Q
from typing import Optional, List, Dict, Callable

from api.engine.ibm_api import translator
from api.data_provider.models import Article
from api.utils.patterns import Json
from api.utils.logger import logger
from api.utils.exceptions import hijack, BackendError

def translate(txt, src, target):
    try:
        return translator.translate(txt, source=src, target=target, return_all=False)
    except Exception as err:
        logger.exception(err)

# def translate_results(results:Json, output_lang:str, fields=None) -> Json:
#     fields = ["title", "body"]
#     for i in range(len(results["hits"]["hits"])):
#         article = results["hits"]["hits"][i]
#         lang = article["language"]
#         if lang == output_lang:
#             continue
#         for key in ("title", "summary"):
#             article[key] = translate(article[key], lang, output_lang)

#     return results

@hijack(BackendError)
def fetch_articles(terms:List[str], 
                   source_language:str,
                   search_languages:Optional[List[str]]=None, 
                   output_language:Optional[str]=None,  # TODO: Unused
                   country:Optional[str]=None,          # TODO: Unused
                   sources:Optional[str]=None,          # TODO: Unused
                   groupby_options:Optional[Json]=None
    ) -> Json:

    if not type(terms) is list:
        raise TypeError("terms must be a list of keywords eg: ['Donald Trump', 'Elections']")
    
    query_terms = ",".join(terms)
    search_languages = search_languages or ["en"]
    if not type(search_languages) is list:
        raise TypeError("search_languages must be a list of language codes eg: ['en', 'nl']")

    translations = {}
    
    # Translate terms in english to minimise risk of missing IBM model
    if source_language != 'en':
        translations[source_language] = query_terms
        query_terms = translate(query_terms, source_language, 'en')

    translations['en'] = query_terms
    logger.debug(query_terms)

    search = Article.search()

    articles = []
    for lang in search_languages:
        if lang not in translations:
            translated = translate(query_terms, 'en', lang)
            if not translated:
                logger.error(f"Could not translate {query_terms} in {lang}")
                continue
            translations[lang] = translated
            logger.debug(translated)
    
        terms = translations[lang].split(",")
        minimum_should_match = int(0.5 * len(terms))

        query = Q(
            'bool', must=Q("match", language=lang), minimum_should_match=minimum_should_match, should=[
                Q("multi_match", fields=['body', 'title'], type='phrase', query=term.strip()) 
                for term in terms
                ]
            )

        query = search.query(query)
        logger.debug(query.to_dict())

        results = query.execute()

        logger.info(f"Got {results.hits.total.value} hits")
        for hit in results:
            logger.info(f"{hit.meta.score}: {hit.title}")
            article = hit.to_dict()
            article["relevance"] = hit.meta.score
            articles.append(article)

    if groupby_options:
        articles = groupby_category(articles, **groupby_options)

    # if output_language is not None:
    #     results = translate_results(results, output_language)

    return {"articles": articles}

def groupby_category(
    results:List[Json],
    key:str, 
    groups:List[Json], 
    default:Optional[str]=None, 
    orderby:Optional[str]=None,
    reverse:Optional[bool]=False, 
    max_results_per_group:Optional[int]=None) -> Json:

    rgroups = {g['value']: g['name'] for g in groups}
    output = OrderedDict({g['name']: [] for g in groups})
    if default:
        output[default] = []
    fget = itemgetter(key)
    for result in results:
        value = fget(result)
        if value in rgroups:
            output[rgroups[value]].append(result)
        elif default:
            output[default].append(result)

    if orderby:
        sortkey = itemgetter(orderby)
        for unsorted in output.values():
            unsorted.sort(key=sortkey, reverse=reverse)

    if max_results_per_group:
        for group in output:
            output[group] = output[group][:max_results_per_group]

    logger.warn(", ".join([f"{k}: {len(v)}" for k, v in output.items()]))
    return output
