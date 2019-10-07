from marshmallow import Schema, fields, pprint

from tests.dev_tests.db.models import Category, Source, Article, Keyword


class CategorySchema(Schema):
    class Meta:
        model = Category
        fields = ("name", "url")


class SourceSchema(Schema):
    class Meta:
        model = Source
        fields = ("id", "name", "lang", "country", "url", "origin", "categories")

    categories = fields.List(fields.Nested(CategorySchema))

class KeywordSchema(Schema):
    class Meta:
        model = Keyword
        fields = ("value",)

class ArticleSchema(Schema):
    class Meta:
        model = Article
        fields = ("title", "publication_date", "url", "source", "keywords")

    source = fields.Nested(SourceSchema)
    keywords = fields.List(fields.Nested(KeywordSchema))


category_schema = CategorySchema()
source_schema = SourceSchema()
keyword_schema = KeywordSchema()
article_schema = ArticleSchema()

categories_schema = CategorySchema(many=True)
sources_schema = SourceSchema(many=True)
keywords_schema = KeywordSchema(many=True)
articles_schema = ArticleSchema(many=True)
