from pprint import pprint
from elasticsearch_dsl import MultiSearch

from api.engine.articles import fetch_articles  #, make_query


# def test_build_query():
#     query_terms = ["Trump", "China", "trade war"]
#     query = make_query(query_terms, "en", ["en", "fr", "nl"])
#     pprint(query.to_dict())
#     response = query.execute()
#     for hit in response:
#         print(hit.meta.score, hit.title)

def test_fetch_articles():
    query = "Donald Trump,China,trade war"
    articles = fetch_articles(query, "en", "en,fr,nl", "en")
    assert type(articles) == list
    assert all(type(article) == dict for article in articles)
    pprint(articles)


if __name__ == '__main__':
    import ipdb; ipdb.set_trace()
    # test_build_query()
    test_fetch_articles()
