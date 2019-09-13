import os.path as p
import json
from copy import deepcopy
from typing import Dict, Any

from api.clients import NewsClient, IBMTranslator, Summary
from api.utils.logger import logger

Json = Dict[str, Any]

LANGUAGES: Dict[str,str] = {
    'en': 'english',
    'nl': 'dutch',
    'de': 'german',
    'fr': 'french'
}

MAX_KEYWORDS: int = 5
SOURCE_FILE: str = "resources/api_sources.json"
MAX_ARTICLES: int = 2

DEFAULT_ERROR_MSG: str = "Houston, we have a problem!"

def format_error(reason:str) -> Dict[str, Dict[str, str]]:
    return {"error": {"text": DEFAULT_ERROR_MSG, "reason": reason}}

def absolute_path(filename:str) -> str:
    return p.join(p.dirname(p.abspath(__file__)), filename)

def process_input(text:str, method:str="remove") -> str:
    
    if method is not "remove":
        raise NotImplementedError(method)

    def flag_word(word:str) -> bool:
        # FIXME: ugly workaround for limited cases (i.e. tweets)
        return any(not(word.startswith(char)) for char in ("#", "@"))

    return " ".join(filter(flag_word, text.split()))

def fetch_articles(params:Json) -> Json:
    """
    Given a dictionary containing an input text, process the text and get relevant
    articles from various sources. The output is formatted in a dictionary with multiple
    elements, the two most important elements are graph (edges and nodes) and a list of articles
    in json format
    """

    logger.debug(f"Request with params {params}")

    output = {
        "graph": {}, 
        "articles": {}, 
        "keywords": [], 
        "language": "", 
        "totalResults": 0}

    text = params["text"]
    translator = IBMTranslator()

    try:
        language = source_lang = translator.identify(text, return_all=False)
        output["language"] = language

        if language != "en":

            try:
                text = translator.translate(text, source=language, target="en", return_all=False)
                language = "en"

            except Exception as err:
                logger.exception(err)
                output["graph"] = output["articles"] = \
                    format_error("The input text could not be translated "
                                 f"from {source_lang} to {language}")
                return output

    except Exception as err:
        logger.exception(err)
        output["graph"] = output["articles"] = format_error("The language could not be identified")
        return output

    text = process_input(text, method="remove")

    with open(absolute_path(SOURCE_FILE)) as f:
        sources = json.load(f)

    sources = {source_group["name"]: source_group["sources"] for source_group in sources}

    try:
        summary = Summary(language=LANGUAGES[language]).fit(text)
        output["graph"] = summary.get_graph()
        output["keywords"] = summary.get_keywords()
        if not len(summary.keywords_):
            raise ValueError("No keywords found")

    except Exception as err:
        logger.exception(err)
        output["graph"] = format_error("Summarisation failed!")
        output["articles"] = format_error("Try with a longer text")
        return output

    try:

        newsapi = NewsClient(
            summary.get_keywords(MAX_KEYWORDS),
            sources=[s for l in sources.values() for s in l],
            start_date=None, 
            end_date=None, 
            language=language
        )

        articles = newsapi.fetch_all()

    except Exception as err:
        logger.exception(err)
        output["articles"] = format_error("Error with the news provider")
        return output

    if not articles["totalResults"]:
        logger.error(f"No articles found: {articles}")
        output["articles"] = format_error(
            "No relevant articles found")
        return output
        
    output["totalResults"] = articles["totalResults"]
    source_map = {source: key
                  for key, sources in sources.items()
                  for source in sources}
    
    sorted_sources = {key: [] for key in sources.keys()}
    for article in articles["articles"]:
        if article["source"]["id"] in source_map:
            sorted_sources[source_map[article["source"]["id"]]].append(article)
    
    articles = {k: v[:MAX_ARTICLES] for k, v in sorted_sources.items()}

    output["articles"] = articles

    return output
