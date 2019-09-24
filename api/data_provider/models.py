from hashlib import md5
from elasticsearch_dsl import InnerDoc, Document, Date, Integer, Keyword, Text, Nested, analyzer

from api.data_provider.__init__ import index_name


html_strip = analyzer('html_strip',
    tokenizer="standard",
    filter=["lowercase", "stop", "snowball"],
    char_filter=["html_strip"]
)

class Source(InnerDoc):
    name = Keyword()
    url = Text()

class Article(Document):
    title = Text(analyzer='snowball', fields={'raw': Keyword()})
    body = Text(analyzer=html_strip)
    tags = Keyword()
    language = Text()
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

