from .api import db


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
    timestamp = db.Column(db.TIMESTAMP())
    text = db.Column(db.Text())
    detected_language = db.Column(db.String(3))
    keywords = db.relationship('Keyword', secondary=text_keyword, lazy='subquery',
        backref=db.backref('keywords', lazy=True))
    articles = db.relationship('Article', secondary=text_article, lazy='subquery',
        backref=db.backref('articles', lazy=True))


class Keyword(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(80), unique=True)


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    articleURL = db.Column(db.String(200))
    author = db.Column(db.String(80))
    description = db.Column(db.Text())
    imageURL = db.Column(db.String(200))
    publication_date = db.Column(db.TIMESTAMP())
    idSource = db.Column(db.ForeignKey('source.id'))

class Source(db.Model):
    id = db.Column(db.String(80), primary_key=True)
    name = db.Column(db.String(80))
    lang = db.Column(db.String(10))
    country = db.Column(db.String(20))


# if __name__ == "__main__":
#     from sqlalchemy import create_engine

#     engine = create_engine(DB_URI)
#     Base.metadata.drop_all(engine)
#     Base.metadata.create_all(engine)