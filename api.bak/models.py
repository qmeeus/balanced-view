import datetime as dt
from marshmallow import fields, pre_load, validate
from sqlalchemy.sql.expression import ClauseElement
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm.collections import attribute_mapped_collection

from .api import db, ma


def get_or_create(session, model, defaults=None, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance, False
    else:
        params = dict((k, v) for k, v in kwargs.items() if not isinstance(v, ClauseElement))
        params.update(defaults or {})
        instance = model(**params)
        session.add(instance)
        return instance, True


class InputText(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=dt.datetime.now)
    text = db.Column(db.Text())
    detected_language = db.Column(db.String(3))

    keywords = association_proxy(
        'text_keywords', 'keyword', 
        creator=lambda k, v: TextKeyword(keyword=k, textrank_score=v)
    )

    articles = association_proxy(
        'text_articles', 'article', 
        creator=lambda k, v: TextArticle(article=k, relevance_score=v)
    )

    def __init__(self, text, detected_language=None):
        self.text = text
        self.detected_language = detected_language


class Keyword(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(80), unique=True)

    def __init__(self, value):
        self.value = value

class Category(db.Model):
    source_id = db.Column(db.ForeignKey('source.id'), primary_key=True)
    name = db.Column(db.String(80), nullable=False, index=True, primary_key=True)
    url = db.Column(db.String(200), nullable=False)

    source = db.relationship("Source", backref="source")

    def __init__(self, source, name, url):
        self.source = source
        self.name = name
        self.url = url


class Source(db.Model):
    id = db.Column(db.String(80), primary_key=True, index=True)
    name = db.Column(db.String(80), index=True)
    lang = db.Column(db.String(10))
    country = db.Column(db.String(20))
    url = db.Column(db.String(200))
    origin = db.Column(db.String(3), default="api")
    categories = db.relationship("Category", backref="category")

    def __init__(self, id, name, lang=None, country=None, url=None, origin=None):
        self.id = id
        self.name = name
        self.lang = lang
        self.country = country
        self.url = url
        self.origin = origin


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    url = db.Column(db.String(200))
    author = db.Column(db.String(200))
    description = db.Column(db.Text())
    image_url = db.Column(db.String(200))
    publication_date = db.Column(db.DateTime)
    source_id = db.Column(db.ForeignKey('source.id'))
    category_name = db.Column(db.String(80))

    source = db.relationship("Source", backref="article_source")

    keywords = association_proxy(
        'article_keywords', 'keyword', 
        creator=lambda k, v: ArticleKeyword(keyword=k, textrank_score=v)
    )

    __table_args__ = (
        db.ForeignKeyConstraint([source_id, category_name], [Category.source_id, Category.name]), 
        {}
    )

    def __init__(self, title=None, url=None, author=None, 
                description=None, image_url=None, publication_date=None, 
                source=None, category_name=None):

        self.title = title
        self.url = url
        self.author = author
        self.description = description
        self.image_url = image_url
        self.publication_date = publication_date
        self.source = source
        self.category_name = category_name


class TextKeyword(db.Model):
    input_text_id = db.Column('input_text_id', db.Integer, db.ForeignKey('input_text.id'), primary_key=True)
    keyword_id = db.Column('keyword_id', db.Integer, db.ForeignKey('keyword.id'), primary_key=True)
    textrank_score = db.Column('textrank_score', db.Float)

    keyword = db.relationship(Keyword)

    input_text = db.relationship(
        InputText, 
        backref=db.backref('text_keywords', 
                           cascade='all, delete-orphan', 
                           collection_class=attribute_mapped_collection("keyword"))
    )

    def __init__(self, input_text=None, keyword=None, textrank_score=None):
        self.input_text = input_text
        self.keyword = keyword
        self.textrank_score = textrank_score


class ArticleKeyword(db.Model):
    article_id = db.Column('article_id', db.Integer, db.ForeignKey('article.id'), primary_key=True)
    keyword_id = db.Column('keyword_id', db.Integer, db.ForeignKey('keyword.id'), primary_key=True)
    textrank_score = db.Column('textrank_score', db.Float)

    keyword = db.relationship(Keyword)

    article = db.relationship(
        Article, 
        backref=db.backref('article_keywords', 
                        cascade='all, delete-orphan', 
                        collection_class=attribute_mapped_collection("keyword"))
    )

    def __init__(self, article=None, keyword=None, textrank_score=None):
        self.article = article
        self.keyword = keyword
        self.textrank_score = textrank_score


class TextArticle(db.Model):
    input_text_id = db.Column('input_text_id', db.Integer, db.ForeignKey('input_text.id'), primary_key=True)
    article_id = db.Column('article_id', db.Integer, db.ForeignKey('article.id'), primary_key=True)
    relevance_score = db.Column('relevance_score', db.Float)

    article = db.relationship(Article)

    input_text = db.relationship(
        InputText, 
        backref=db.backref('text_articles', 
                           cascade='all, delete-orphan', 
                           collection_class=attribute_mapped_collection("article"))
    )

    def __init__(self, input_text=None, article=None, relevance_score=None):
        self.input_text = input_text
        self.article = article
        self.relevance_score = relevance_score


class InputTextSchema(ma.Schema):
    class Meta:
        fields = ("text", "timestamp", "detected_language", "keywords", "articles")

class CategorySchema(ma.Schema):
    class Meta:
        model = Category
        fields = ("name", "url")

class SourceSchema(ma.Schema):
    class Meta:
        model = Source
        fields = ("id", "name", "lang", "country", "url", "categories")

    categories = fields.List(fields.Nested(CategorySchema))

class ArticleSchema(ma.Schema):
    class Meta:
        model = Article
        fields = ("title", "url", "author", "description", "image_url", "publication_date", "source", "category")

    source = fields.Nested(SourceSchema)
    category = fields.Nested(CategorySchema)