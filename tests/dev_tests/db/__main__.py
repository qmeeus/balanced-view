from flask import jsonify
import json
import random

from api.models import get_or_create
from tests.dev_tests.db.__init__ import app
from tests.dev_tests.db.models import Category, Source, Article, Keyword, db
from tests.dev_tests.db.schema import categories_schema, sources_schema, articles_schema, keywords_schema
from tests.utils import load_rss_sources, load_articles, load_texts

@app.route('/')
def index():
    return "<br>".join([
        f"<a href='dump_{table}'>Dump {table.title()}</a>" 
        for table in ("category", "source", "article", "keyword")])


@app.route('/dump_category')
def dump_category():
    category = Category.query.all()
    return jsonify(categories_schema.dump(category))

@app.route('/dump_source')
def dump_source():
    source = Source.query.all()
    return jsonify(sources_schema.dump(source))

@app.route('/dump_article')
def dump_article():
    article = Article.query.all()
    return jsonify(articles_schema.dump(article))

@app.route('/dump_keyword')
def dump_keyword():
    keyword = Keyword.query.all()
    return jsonify(keywords_schema.dump(keyword))


def build_db():
    db.drop_all()
    db.create_all()

    for source_json in load_rss_sources()["sources"]:
        categories = source_json.pop("categories")
        source = Source(**source_json)
        db.session.add(source)
        
        for category_json in categories:
            category = Category(source=source, **category_json)
            db.session.add(category)

    db.session.commit()

    alphabet = "abcdefghijklmnopqrstuvwxyz"

    for article_json in load_articles()["articles"]:
        article = Article(
            title=article_json["title"], 
            url=article_json["link"], 
            description=article_json["summary"], 
            source=db.session.query(Source).get("vrt")
        )

        for _ in range(random.randint(3, 8)):
            kw_val = "".join([random.choice(alphabet) for _ in range(random.randint(5, 15))])
            article.keywords[Keyword(kw_val)] = random.random()

        db.session.add(article)
    
    db.session.commit()



@app.before_first_request
def first_request():
    build_db()


app.run(debug=True, port=7777)