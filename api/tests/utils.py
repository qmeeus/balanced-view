import os.path as p
import json


DATA_DIR = p.join(p.dirname(__file__), "test_data")


def load_keywords():
    with open(p.join(DATA_DIR, "keywords.txt")) as f:
        lines = list(filter(bool, map(str.strip, f.readlines())))
        yield from map(str.split, lines)

def load_rss_sources():
    with open(p.join(DATA_DIR, "rss_sources.json")) as f:
        return json.load(f)


def get_more_data():
    from api.data_provider.sources.rss_spider import RssFetcher

    collection = RssFetcher.from_file()
    all_results = list(zip(*collection.fetch_all()))[-1]
    of = p.join(p.dirname(__file__), "../test_data/articles.json")
    with open(of, 'w') as f:
        json.dump({"articles": all_results}, f)

def load_texts():

    def fmap(text):
        text = text.strip()
        if not text:
            return None
        lang, text = text.split("\n", maxsplit=1)
        return lang, text

    with open(p.join(DATA_DIR, "texts.txt")) as f:
        raw = f.read()

    yield from filter(bool, map(fmap, raw.split("\n\n")))