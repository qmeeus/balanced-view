import os.path as p
import traceback
import sys
import json


DATA_DIR = p.join(p.dirname(__file__), "test_data")


def load_keywords():
    with open(p.join(DATA_DIR, "keywords.txt")) as f:
        lines = list(filter(bool, map(str.strip, f.readlines())))
        yield from map(str.split, lines)


def load_texts(filename="texts.txt"):

    def fmap(text):
        text = text.strip()
        if not text:
            return None
        lang, text = text.split("\n", maxsplit=1)
        return lang, text

    with open(p.join(DATA_DIR, filename)) as f:
        raw = f.read()

    yield from filter(bool, map(fmap, raw.split("\n\n")))

def load_rss_sources():
    return load_json("rss_sources.json")


def load_articles():
    articles_json = load_json("articles.json")
    for article_json in articles_json["articles"]:
        yield article_json["summary"]


def load_json(filename):
    with open(p.join(DATA_DIR, filename)) as f:
        return json.load(f)


def debug(debugger=False):
    def _debug(func):
        def wrapper(*args):
            print(f"Call {func.__name__}:", *args)
            if debugger:
                import ipdb; ipdb.set_trace()
            retval = func(*args)
            print("Return value:", retval)
            return retval
        return wrapper
    return _debug


def safe(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            traceback.print_exc(file=sys.stdout)
    return wrapper
