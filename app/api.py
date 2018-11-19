import os
import re
from summa import keywords
from newsapi import NewsApiClient


def load_key():
    dirname = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(dirname, "apikey")) as f:
        return f.read().strip()

def load_sources(language="en"):
    # return 'bbc-news,the-verge'
    return "msnbc,cnn"

def fetch_articles(text, start_date=None, end_date=None, language=None):

    newsapi = NewsApiClient(api_key=load_key())
    kws = keywords.keywords(text, words=3).replace("\n", " ")
    print(kws)
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
