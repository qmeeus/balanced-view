from elasticsearch_dsl import InnerDoc, Document, Date, Integer, Keyword, Text, Nested, analyzer, Float

from api.data_provider.__init__ import index_name


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
        name = index_name
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

    class Index:
        name = index_name
        settings = {
          "number_of_shards": 2,
        }


# When elasticsearch is empty, we need to create the index
# but this will throw an error if the index was already created
for object_type in (Article, InputText):
    try:
        object_type.init()
    except:
        pass
