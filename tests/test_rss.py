import operator
import feedparser
from api.clients.rss import RSSFeed


SOURCE_FILE = "api/resources/rss_sources.json"


def _test_list(obj, non_empty=True, element_type=str):
    assert type(obj) == list, "Object is not a list"
    if non_empty:
        assert len(obj) > 0, "List is empty"
    assert all(map(lambda it: type(it) is element_type, obj)), \
        f"Not all items are of type {element_type}"


def test_constructor():
    rss_feed = RSSFeed(SOURCE_FILE)
    assert isinstance(rss_feed, RSSFeed)

    assert hasattr(rss_feed, "sources")
    _test_list(rss_feed.sources, element_type=dict)


def test_accessors():
    rss_feed = RSSFeed(SOURCE_FILE)
    source_ids = rss_feed._filter(rss_feed.sources, return_value="id")
    _test_list(source_ids)

    source_names = rss_feed.available_sources
    _test_list(source_names)

    selected_source = rss_feed[source_ids[0]]
    assert type(selected_source) == dict
    
    selected_sources = rss_feed.get(name=source_names[0])
    _test_list(selected_sources, element_type=dict)

    selected_sources = rss_feed._filter(rss_feed.sources, lang="nl", country="be")
    _test_list(selected_sources, element_type=dict)

def test_feeds():
    rss_feed = RSSFeed(SOURCE_FILE)
    for source_id in rss_feed._filter(rss_feed.sources, return_value="id"):
        feeds = rss_feed.get_feeds(source_id)
        _test_list(feeds, element_type=feedparser.FeedParserDict)
        import ipdb; ipdb.set_trace()


if __name__ == "__main__":
    test_feeds()
