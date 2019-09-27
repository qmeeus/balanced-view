import os
from elasticsearch_dsl import Search, MultiSearch, Q
from typing import Optional, List

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
def fetch_articles(terms:str, 
                   source_language:str,
                   search_languages:Optional[str]="en", 
                   output_language:Optional[str]=None,  # TODO: Unused
                   country:Optional[str]=None,          # TODO: Unused
                   sources:Optional[str]=None           # TODO: Unused
    ) -> List[Json]:
    
    translations = {}
    for lang in search_languages.split(","):
        if lang != source_language:
            translated = translate(terms, source_language, lang)
            if not translated:
                continue
        else:
            translated = terms

        translations[lang] = list(map(str.strip, translated.split(",")))
        logger.debug(translated)

    query = Q('bool', should=[
        Q('bool', must=Q("match", language=lang), minimum_should_match=2, should=[
            Q("match_phrase", **{attr: term}) 
            for attr in ('body', 'title')
            for term in translated
        ]) for lang, translated in translations.items()
    ])

    search = Article.search().query(query)
    logger.debug(search.to_dict())

    response = search.execute()

    for hit in response:
        print(hit.meta.score, hit.title)

    # if output_language is not None:
    #     results = translate_results(results, output_language)

    return {"articles": list(map(Article.to_dict, response))}

