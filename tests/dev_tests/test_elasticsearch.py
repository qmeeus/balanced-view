from elasticsearch import Elasticsearch
from tests.utils import load_json


es = Elasticsearch([{'host': 'localhost','port': 9200}])

# es.indices.create(index='article-index', ignore=400)

# for i, article in enumerate(load_json("articles.json")["articles"]):
#     res = es.index(index="article-index", doc_type="article", id=i+1, body=article)
#     print(res)

def search_in_summary(query):
    return es.search(index='article-index', body={'query': {'match': {'summary': query}}})

for result in search_in_summary("maffia Amsterdam")["hits"]["hits"]:
    print(f"[ Score: {result['_score']} ]", result["_source"]["title"])
    print(result["_source"]["summary"])
    print()

