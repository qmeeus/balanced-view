from flask import request, jsonify
from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from datetime import datetime as dt
from time import mktime
import json

from api.engine.articles import fetch_articles
from api.engine.spider import SourceCollection
from api.models import db, get_or_create
from api.models import Keyword, InputText, Article, Source, Category, TextKeyword, ArticleKeyword
from api.models import SourceSchema, CategorySchema
from api.utils.logger import logger

DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

class BalancedView(Resource):

    def __init__(self):
        self.parser = RequestParser()
        self.parser.add_argument('text', type=str, required=True)

    def post(self):
        params = self.parser.parse_args()
        output = fetch_articles(params)
        text = InputText(text=params["text"], detected_language=output["language"])

        if output["keywords"]:
            for kwd_dict in output["keywords"]:
                kwd_val, score = kwd_dict['keyword'], kwd_dict['score']
                keyword, _ = get_or_create(db.session, Keyword, value=kwd_val)
                text.keywords[keyword] = score

        if "error" not in output["articles"]:
            text.totalResults=output["totalResults"]
            for articles_collection in output["articles"].values():
                for result in articles_collection:
                    source, _ = get_or_create(
                        db.session, Source, 
                        defaults={'name': result["source"]["name"]}, 
                        id=result["source"]["id"])
                    db.session.flush()

                    publication_date = dt.strptime(result["publishedAt"], DATE_FORMAT)
                    article, _ = get_or_create(
                        db.session, Article,
                        defaults={
                            'url': result["url"],
                            'author': result["author"],
                            'description': result["description"],
                            'image_url': result["urlToImage"],
                            'source': source},
                        title=result["title"], publication_date=publication_date)

                    text.articles[article] = 0

        db.session.add(text)
        db.session.commit()
                            
        return output


class DataFetcher(Resource):

    def __init__(self):
        self.sources_schema = SourceSchema(many=True)

    def post(self):
        json_data = request.get_json(force=True)
        if not json_data:
            return {'message': 'No input data provided'}, 400

        try:
            sources = self.sources_schema.load(json_data["sources"])

        except Exception as err:
            logger.exception(err)
            return {'message': 'Malformed JSON'}, 400

        collection = SourceCollection(sources)
        for source_item in collection:
            source, _ = get_or_create(
                db.session, Source, 
                defaults={"origin": "rss"}.update(source_item.to_dict()), 
                id=source_item.id)
            db.session.flush()

            for category_item in source_item:
                category, _ = get_or_create(
                    db.session, Category, 
                    defaults=category_item,
                    name=category_item["name"], source=source)

        db.session.commit()
        
        for source_id, category_name, keywords, article_json in collection.fetch_all():

            category = db.session.query(Category).filter_by(
                name=category_name, source_id=source_id).first()

            if category is None:
                logger.error(f"Category not found: {source_id}/{category_name}")
                raise KeyError(f"Category({source_id}/{category_name})")

            pub_date = dt.fromtimestamp(mktime(article_json["published_parsed"]))
            image_urls = [link["href"] 
                          for link in article_json['links'] 
                          if link["type"].startswith("image")]

            image_url = image_urls[0] if len(image_urls) else None                
            article, _ = get_or_create(
                db.session, Article, 
                defaults={
                    'title': article_json["title"],
                    'url': article_json["link"],
                    'description': article_json["summary"],
                    'image_url': image_url,
                    'publication_date': pub_date,
                    'source': category.source,
                    'category_name': category.name
                },
                title=article_json["title"], publication_date=pub_date)
        
            for keyword_dict in keywords:
                kw_val, score = keyword_dict['keyword'], keyword_dict['score']
                keyword, _ = get_or_create(db.session, Keyword, value=kw_val)
                # article.keywords[keyword] = score
                assoc_art_kw = get_or_create(db.session, ArticleKeyword, 
                                             article=article, keyword=keyword, 
                                             defaults={'textrank_score': score})

        db.session.commit()

        return jsonify({"message": "Success"})
