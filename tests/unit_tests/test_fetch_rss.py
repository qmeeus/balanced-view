import datetime as dt
from time import time
from api.data_provider.sources.rss_spider import RssFeed
from api.utils.logger import logger
from tests.utils import load_rss_sources

def _test_output(output, print_output=False):
    assert type(output) is dict
    expected = [("source", dict), ("category", str), ("title", str), ("body", str), ("publication_date", dt.datetime)]
    for key, typ in expected:
        assert key in output, key
        assert type(output[key]) == typ, output[key]

    if print_output:
        logger.debug(output["title"])
        logger.debug(output["body"])


def test_source():

    example = load_rss_sources()['sources'][0]

    feed = RssFeed.from_dict(example)
    assert isinstance(feed, RssFeed)

    assert all(type(c) is dict for c in feed)

    cats = feed.available_categories
    assert type(cats) is list

    obj = feed.to_dict()
    assert type(obj) is dict

    for result in feed.get_latest(["Headlines"]):
        _test_output(result, print_output=True)


    start = time()
    feed.N_THREADS = 1
    for result in feed.get_latest():
        _test_output(result)
    logger.debug(f"Job took {time() - start:.2f} s")

    start = time()
    feed.N_THREADS = 12
    for result in feed.get_latest():
        _test_output(result)
    logger.debug(f"Job took {time() - start:.2f} s")


if __name__ == "__main__":
    # import ipdb; ipdb.set_trace()
    test_source()
