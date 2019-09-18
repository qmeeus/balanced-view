import datetime as dt
from marshmallow import fields, pre_load, validate
from sqlalchemy.sql.expression import ClauseElement

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


class TextKeywords(db.Model):
    input_text_id = db.Column('input_text_id', db.Integer, db.ForeignKey('input_text.id'), primary_key=True)
    keyword_id = db.Column('keyword_id', db.Integer, db.ForeignKey('keyword.id'), primary_key=True)
    textrank_score = db.Column('textrank_score', db.Float)


class ArticleKeywords(db.Model):
    article_id = db.Column('article_id', db.Integer, db.ForeignKey('article.id'), primary_key=True)
    keyword_id = db.Column('keyword_id', db.Integer, db.ForeignKey('keyword.id'), primary_key=True)
    textrank_score = db.Column('textrank_score', db.Float)


class TextArticles(db.Model):
    input_text_id = db.Column('input_text_id', db.Integer, db.ForeignKey('input_text.id'), primary_key=True)
    article_id = db.Column('article_id', db.Integer, db.ForeignKey('article.id'), primary_key=True)
    relevance_score = db.Column('relevance_score', db.Float)


class InputText(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=dt.datetime.now)
    text = db.Column(db.Text())
    detected_language = db.Column(db.String(3))

    keywords = db.relationship('Keyword', secondary='TextKeywords', lazy='subquery',
        backref=db.backref('keywords', lazy=True))
    
    articles = db.relationship('Article', secondary='TextArticles', lazy='subquery',
        backref=db.backref('articles', lazy=True))


class Keyword(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(80), unique=True)

class Category(db.Model):
    source_id = db.Column(db.ForeignKey('source.id'), primary_key=True)
    name = db.Column(db.String(80), nullable=False, index=True, primary_key=True)
    url = db.Column(db.String(200), nullable=False)

class Source(db.Model):
    id = db.Column(db.String(80), primary_key=True, index=True)
    name = db.Column(db.String(80), index=True)
    lang = db.Column(db.String(10))
    country = db.Column(db.String(20))
    url = db.Column(db.String(200))
    origin = db.Column(db.String(3), default="api")
    categories = db.relationship("Category", backref="category")

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

    keywords = db.relationship('Keyword', secondary='ArticleKeywords', lazy='subquery',
            backref=db.backref('keywords', lazy=True))

    __table_args__ = (db.ForeignKeyConstraint(
        [source_id, category_name], [Category.source_id, Category.name]), 
        {})

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