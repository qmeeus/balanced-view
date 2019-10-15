import datetime as dt
from elasticsearch_dsl import InnerDoc, Document, Date, Integer, Keyword, Text, Nested, analyzer, Float


html_strip = analyzer('html_strip',
    tokenizer="standard",
    filter=["lowercase", "stop", "snowball"],
    char_filter=["html_strip"]
)

class Source(InnerDoc):
    name = Keyword()
    url = Text()
    language = Text()
    country = Text()

class Article(Document):
    title = Text(analyzer='snowball', fields={'raw': Keyword()})
    body = Text(analyzer=html_strip)
    tags = Keyword()
    language = Text()
    country = Text()
    publication_date = Date()
    source = Nested(Source)
    category = Keyword()
    url = Text()
    image_url = Text()

    class Index:
        name = "article-index"
        settings = {
          "number_of_shards": 2,
        }

class DetectedKeyword(InnerDoc):
    keyword = Keyword()
    score = Float()

class Topic(InnerDoc):
    topic = Keyword()
    score = Float()

class InputText(Document):
    body = Text(analyzer=html_strip)
    language = Text()
    keywords = Nested(DetectedKeyword)
    topics = Nested(Topic)
    request_date = Date()

    class Index:
        name = "input-index"
        settings = {
          "number_of_shards": 2,
        }

    def save(self, **kwargs):
        self.request_date = dt.datetime.now()
        return super().save(**kwargs)


# When elasticsearch is empty, we need to create the index
# but this will throw an error if the index was already created
for object_type in (Article, InputText):
    try:
        object_type.init()
    except:
        pass
