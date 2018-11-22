import os
import re
import json
from summa import keywords
from newsapi import NewsApiClient


def get_keywords(text, n_words, language='en', split=False, scores=False):
    try:
        return keywords.keywords(text, words=n_words, split=split, scores=scores)
    except IndexError:
        return [] if split else ""

def fetch_articles(text, start_date=None, end_date=None, language=None, n_words=3):

    newsapi = NewsApiClient(api_key=load_key())
    kws = get_keywords(text, n_words, language).replace("\n", " ")
    return newsapi.get_everything(
        q=kws,
        sources=load_sources(language=language),
        # domains='bbc.co.uk,techcrunch.com',
        from_param=start_date or None,
        to=end_date or None,
        language=language or None,
        sort_by='relevancy',
        # page=2
    )

def absolute_path(filename):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)

def load_key():
    with open(absolute_path("apikey")) as f:
        return f.read().strip()

def load_sources(influence="all", language="en"):
    with open(absolute_path("api_sources.json")) as f:
        sources = json.load(f)
    
    if influence == "all":
        sources_list = [s for l in sources.values() for s in l]
    else:
        assert influence in sources.keys(), "{} not in available political leanings".format(influence)
        sources_list = sources[influence]
    return ",".join(sources_list)


if __name__ == "__main__":
    # Test API
    text = """Democrat Stacey Abrams acknowledges that Republican Brian Kemp will be certified as 
    the next Georgia governor, but says she is not offering a speech of concession because that 
    would suggest the election process was just: "The state failed its voters" - @MSNBC"""
    articles = fetch_articles(text, "2018-11-01")
    print(articles["status"] + "... " + str(articles["totalResults"]) + " results")
    for article in articles["articles"]:
        print(article["source"]["name"])
        print(article["title"])
        
    with open(absolute_path('results.json'), 'w') as f:
        json.dump(articles, f)
