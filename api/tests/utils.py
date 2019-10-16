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


def get_more_data(output_file=None):
    from api.data_provider.sources.rss_spider import RssFetcher

    output_file = output_file or 'articles.json'

    if not any(output_file.endswith(ext) for ext in ('json', 'txt')):
        raise ValueError("Invalid output format")

    filename = p.join(DATA_DIR, output_file)

    collection = RssFetcher.from_file()
    articles = list(collection.fetch_all())
    with open(filename, 'w') as f:
        if output_file.endswith('json'):    
            json.dump({"articles": articles}, f)
        else:
            for article in articles:
                f.write(f"{article['language']}\n{article['title'].strip()}\n{article['body'].strip()}\n\n")

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


if __name__ == '__main__':
    import sys
    get_more_data(sys.argv[1] if len(sys.argv) > 1 else None)
