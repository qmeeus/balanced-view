import os.path as p
from operator import itemgetter, attrgetter
import json
from time import time

from api.engine.spider import Source, SourceCollection
from tests.unit_tests.test_fetch_rss import _test_output
from tests.utils import load_rss_sources


def get_more_data():
    
    collection = SourceCollection.from_file()

    all_results = list(zip(*collection.fetch_all()))[-1]
    with open(p.join(p.dirname(__file__), "../test_data/articles.json"), 'w') as f:
        json.dump({"articles": all_results}, f)


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

    # start = time()
    # for result in collection.fetch_all(**filters):
    #     _test_output(result, print_output=False)
    # print(f"Job took {time() - start}")

    start = time()
    for result in collection.fetch_all():
        _test_output(result, print_output=False)
    print(f"Job took {time() - start}")


if __name__ == "__main__":
    # import ipdb; ipdb.set_trace()
    test_source_collection()
    # get_more_data()
