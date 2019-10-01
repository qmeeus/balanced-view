import os
from collections import defaultdict
from operator import itemgetter
from elasticsearch_dsl import Search, MultiSearch, Q
from typing import Optional, List, Dict, Callable

from api.engine.ibm_api import translator
from api.data_provider import index_name
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
    ) -> List[Json]:

    translations = {}
    terms = ",".join(terms)
    search_languages = search_languages or ["en"]

    # Translate terms in english to minimise risk of missing IBM model
    if source_language != 'en':
        translations[source_language] = terms
        terms = translate(terms, source_language, 'en')

    translations['en'] = terms
    logger.debug(terms)

    for lang in search_languages:
        if lang not in translations:
            translated = translate(terms, 'en', lang)
            if not translated:
                continue
            translations[lang] = translated
            logger.debug(translated)
    
    query = Q('bool', should=[
        Q('bool', must=Q("match", language=lang), minimum_should_match=2, should=[
            Q("match_phrase", **{attr: term.strip()}) 
            for attr in ('body', 'title')
            for term in translated.split(',')
        ]) for lang, translated in translations.items()
    ])

    search = Article.search().query(query)
    logger.debug(search.to_dict())

    response = search.execute()

    for hit in response:
        print(hit.meta.score, hit.title)

    articles = list(map(Article.to_dict, response))

    if groupby_options:
        return {"articles": groupby_category(articles, **groupby_options)}

    # if output_language is not None:
    #     results = translate_results(results, output_language)

    return {"articles": articles}

def groupby_category(results:List[Json], key:str, groups:List[Json], default:Optional[str]=None):
    rgroups = {g['value']: g['name'] for g in groups}
    output = defaultdict(list)
    fget = itemgetter(key)
    for result in results:
        value = fget(result)
        if value in rgroups:
            output[rgroups[value]].append(result)
        elif default:
            output[default].append(result)
    return output
