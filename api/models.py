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


text_keyword = db.Table('text_keywords',
    db.Column('input_text_id', db.Integer, db.ForeignKey('input_text.id'), primary_key=True),
    db.Column('keyword_id', db.Integer, db.ForeignKey('keyword.id'), primary_key=True)
)

text_article = db.Table('text_articles',
    db.Column('input_text_id', db.Integer, db.ForeignKey('input_text.id'), primary_key=True),
    db.Column('article_id', db.Integer, db.ForeignKey('article.id'), primary_key=True)
)


class InputText(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=dt.datetime.now)
    text = db.Column(db.Text())
    detected_language = db.Column(db.String(3))
    keywords = db.relationship('Keyword', secondary=text_keyword, lazy='subquery',
        backref=db.backref('keywords', lazy=True))
    articles = db.relationship('Article', secondary=text_article, lazy='subquery',
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