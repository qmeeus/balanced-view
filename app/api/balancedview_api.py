import os.path as p
import json

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

    text = process_input(params["text"], method="remove")

    with open(absolute_path(SOURCE_FILE)) as f:
        sources = json.load(f)

    sources = {source_group["name"]: source_group["sources"] for source_group in sources}

    try:
        summary = Summary(
            text, 
            language=LANGUAGES[params['language']]
        )

        output["graph"] = summary.get_graph()

    except Exception as err:
        output["graph"] = {"error": {
            "text": "Summarisation failed!",
            "reason": str(err)
        }}

    if "error" in output["graph"] or not len(summary.keywords):
        output["articles"] = {"error": {
            "text": "Keyword extraction failed!",
            "reason": "One frequent explanation is that the text is too short."
        }}

        return output

    try:

        newsapi = NewsClient(
            summary.get_keywords(MAX_KEYWORDS), 
            ",".join([s for l in sources.values() for s in l]), 
            format_date(start_date), 
            format_date(end_date), 
            params['language']
        )

    except Exception as err:
        print(err)
        output["articles"] = {"error": {
            "text": "API error!",
            "reason": "It is possible that the api key was not found or is expired or we have reached our limit."
        }}
        return output

    if not newsapi.articles["totalResults"]:
        output["articles"] = {"error": {
            "text": "Search yielded no results!",
            "reason": "We could not find related articles in any of the sources."
        }}
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
