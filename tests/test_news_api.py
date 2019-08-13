from app.api.clients import NewsClient


keywords = "trump republican shootings el paso"
sources = "cnn,fox-news,politico"
start_date, end_date = "2019-08-13", "2019-07-13"
language = "en"
newsapi = NewsClient(keywords, sources, start_date, end_date, language)

assert hasattr(newsapi, "articles")
assert type(newsapi.articles) == dict

print("Status:", newsapi.articles["status"])
print("Total results:", newsapi.articles["totalResults"])

for article in newsapi.articles["articles"]:
    print(article["source"]["name"], ":", article["title"])
