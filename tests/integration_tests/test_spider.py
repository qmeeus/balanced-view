import os.path as p
from operator import itemgetter, attrgetter
from api.engine.spider import Source, SourceCollection



def test_source():
    example =  {
        "name": "vrt-nieuws", 
        "id": "vrt", 
        "url": "https://www.vrt.be",
        "country": "be",
        "lang": "nl",
        "categories": [
            {
                "name": "Headlines", 
                "url": "/vrtnws/nl.rss.headlines.xml"
            },
            {
                "name": "Latest", 
                "url": "/vrtnws/nl.rss.articles.xml"
            },
        ]
    }

    source = Source.from_dict(example)
    assert isinstance(source, Source)

    assert all(type(c) is dict for c in source)

    cats = source.available_categories
    assert type(cats) is list

    obj = source.to_dict()
    assert type(obj) is dict

    for result in source.get_latest(["Headlines"]):
        print(len(result))

def test_source_collection():
    collection = SourceCollection.from_file()
    assert isinstance(collection, SourceCollection)
    assert all(isinstance(s, Source) for s in collection)

    item = collection["vrt"]
    assert isinstance(item, Source)

    assert "vrt" in collection

    assert type(collection.available_sources) is list

    filters = {"lang": "nl", "country": "be"}
    sources = collection.find_all(**filters)
    assert all(isinstance(s, Source) for s in sources)
    assert len(sources)

    filters = dict(id=["vrt", "standaard"], **filters)
    sources = collection.find_all(**filters)
    assert all(isinstance(s, Source) for s in sources)
    assert len(sources)

    categories = ["Headlines", "Latest", "Buitenland"]
    sources = collection.find_all(categories=categories)
    assert all(isinstance(s, Source) for s in sources)
    assert all(
        all(
            c in categories for c in s.available_categories
        ) for s in sources
    )

    filters = dict(categories=categories, **filters)
    sources = collection.find_all(**filters)
    assert len(sources)
    assert all(isinstance(s, Source) for s in sources)

    i = 5
    for name, cat, res in collection.fetch_all(**filters):
        print(name, cat, len(res))
        i -= 1 
        if not(i): break


if __name__ == "__main__":
    import ipdb; ipdb.set_trace()
    test_source()
    test_source_collection()
