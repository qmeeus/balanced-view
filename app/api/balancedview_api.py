import os.path as p
import json
from copy import deepcopy
from datetime import date
from dateutil.relativedelta import relativedelta

from .clients import NewsClient, IBMTranslator, Summary


LANGUAGES = {
    'en': 'english',
    'nl': 'dutch',
    'de': 'german',
    'fr': 'french'
}

MAX_KEYWORDS = 5
SOURCE_FILE = "api_sources.json"
MAX_ARTICLES = 2

UNKNOWN_LANG_ERROR = {"error": {"text": "The language could not be identified", "reason": None}}
TRANSLATION_ERROR = {"error": {"text": "The input text could not be translated", "reason": None}}
SUMMA_ERROR = {"error": {"text": "Summarisation failed!", "reason": None}}
NO_KEYWORDS_ERROR = {"error": {"text": "Keyword extraction failed!", "reason": None}}
NEWSAPI_ERROR = {"error": {"text": "Keyword extraction failed!", "reason": None}}
NO_RESULTS_ERROR = {"error": {"text": "Keyword extraction failed!", "reason": None}}

def format_error(error, reason):
    error = deepcopy(error)
    error["error"]["reason"] = reason
    return error

def absolute_path(filename):
    return p.join(p.dirname(p.abspath(__file__)), filename)

def format_date(date):
    return date.strftime('%Y-%m-%d')

def process_input(text, method="remove"):

    def flag_word(word):
        return word[0] not in ["#", "@"]

    return " ".join(filter(flag_word, text.split()))
    

def run(params):

    output = {"graph": {}, "articles": {}}

    end_date = date.today()
    start_date = end_date - relativedelta(months=1)

    text = params.pop("text")
    translator = IBMTranslator()

    try:
        language = translator.identify(text, return_all=False)
        if language != "en":
            try:
                text = translator.translate(text, source=language, target="en", return_all=False)
                language = "en"
            except Exception as err:
                output["graph"] = output["articles"] = format_error(TRANSLATION_ERROR, str(err))
                return output
    except Exception as err:
        output["graph"] = output["articles"] = format_error(UNKNOWN_LANG_ERROR, str(err))
        return output

    text = process_input(text, method="remove")

    with open(absolute_path(SOURCE_FILE)) as f:
        sources = json.load(f)

    sources = {source_group["name"]: source_group["sources"] for source_group in sources}

    try:
        summary = Summary(
            text, 
            language=LANGUAGES[language]
        )

        output["graph"] = summary.get_graph()

    except Exception as err:
        output["graph"] = format_error(SUMMA_ERROR, str(err))

    if "error" in output["graph"] or not len(summary.keywords):
        output["articles"] = format_error(NO_KEYWORDS_ERROR, "Try with a longer text")
        return output

    try:

        newsapi = NewsClient(
            summary.get_keywords(MAX_KEYWORDS), 
            ",".join([s for l in sources.values() for s in l]), 
            format_date(start_date), 
            format_date(end_date), 
            language
        )

    except Exception as err:
        print(err)
        output["articles"] = format_error(NEWSAPI_ERROR, str(err))
        return output

    if not newsapi.articles["totalResults"]:
        output["articles"] = format_error(NO_RESULTS_ERROR, "We could not find related articles in any of the sources.")
        return output
        
    source_map = {source: key
                  for key, sources in sources.items()
                  for source in sources}
    
    sorted_sources = {key: [] for key in sources.keys()}
    for article in newsapi.articles["articles"]:
        if article["source"]["id"] in source_map:
            sorted_sources[source_map[article["source"]["id"]]].append(article)
    
    articles = {k: v[:MAX_ARTICLES] for k, v in sorted_sources.items()}

    output["articles"] = articles

    return output
