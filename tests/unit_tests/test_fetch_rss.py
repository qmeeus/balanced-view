from time import time
from api.engine.spider import Source
from tests.utils import load_rss_sources

def _test_output(output, print_output=False):
    assert len(output) == 4
    id, category, keywords, article = output
    assert type(id) is str
    assert type(category) is str
    assert type(keywords) is list
    assert all(type(kw) is dict for kw in keywords)
    assert isinstance(article, dict)
    if print_output:
        print(article.summary)
        print("Keywords:", ", ".join(["{keyword} ({score:.2f})".format(**kw) for kw in keywords]))


def test_source():

    example = load_rss_sources()['sources'][0]

    source = Source.from_dict(example)
    assert isinstance(source, Source)

    assert all(type(c) is dict for c in source)

    cats = source.available_categories
    assert type(cats) is list

    obj = source.to_dict()
    assert type(obj) is dict

    for result in source.get_latest(["Headlines"]):
        _test_output(result, print_output=True)


    start = time()
    source.N_THREADS = 1
    for result in source.get_latest():
        _test_output(result)
    print(f"Job took {time() - start:.2f} s")

    start = time()
    source.N_THREADS = 12
    for result in source.get_latest():
        _test_output(result)
    print(f"Job took {time() - start:.2f} s")


if __name__ == "__main__":
    # import ipdb; ipdb.set_trace()
    test_source()
