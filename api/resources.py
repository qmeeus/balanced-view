from flask import request, jsonify
from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from datetime import datetime as dt
from time import mktime
import json

from api.engine.articles import fetch_articles
from api.engine.spider import SourceCollection
from api.models import db, Keyword, InputText, Article, Source, Category
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
        text = InputText(
            text=params["text"], 
            timestamp=dt.now(), 
            detected_language=output["language"])

        if output["keywords"]:
            for kwd_val in output["keywords"]:
                kwd = db.session.query(Keyword).filter_by(value=kwd_val).first()
                if not kwd:
                    kwd = Keyword(value=kwd_val)
                    db.session.add(kwd)
                text.keywords.append(kwd)

        if "error" not in output["articles"]:
            text.totalResults=output["totalResults"]
            for articles_collection in output["articles"].values():
                for result in articles_collection:
                    article = db.session.query(Article).filter_by(
                        title=result["title"], publication_date=result["publishedAt"]).first()
                    if not article:
                        source = db.session.query(Source).get(result["source"]["id"])
                        if not source:
                            source = Source(
                                id=result["source"]["id"], 
                                name=result["source"]["name"])
                            db.session.add(source)
                            db.session.flush()
                        
                        article = Article(
                            title=result["title"],
                            url=result["url"],
                            author=result["author"],
                            description=result["description"],
                            image_url=result["urlToImage"],
                            publication_date=dt.strptime(result["publishedAt"], DATE_FORMAT),
                            source_id=source.id)
                        db.session.add(article)

                    text.articles.append(article)

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
            source = db.session.query(Source).get(source_item.id)
            if not source:
                source = Source(**source_item.to_dict())
                db.session.add(source)
                db.session.flush()

            for category_item in source_item:
                category = db.session.query(Category).filter_by(
                    name=category_item["name"], source_id=source.id).first()
                if not category:
                    category = Category(source_id=source.id, **category_item)
                    db.session.add(category)

        db.session.commit()
        
        for source_id, category_name, results in collection.fetch_all():

            category = db.session.query(Category).filter_by(
                name=category_name, source_id=source_id).first()

            if category is None:
                logger.error(f"Category not found: {source_id}/{category_name}")
                raise KeyError(f"Category({source_id}/{category_name})")

            for result in results:
                pub_date = dt.fromtimestamp(mktime(result["published_parsed"]))
                article = db.session.query(Article).filter_by(
                    title=result["title"], publication_date=pub_date).first()
                if not article:
                    image_urls = [link["href"] 
                                  for link in result['links'] 
                                  if link["type"].startswith("image")]

                    image_url = image_urls[0] if len(image_urls) else None
                    article = Article(
                        title=result["title"],
                        url=result["link"],
                        description=result["summary"],
                        image_url=image_url,
                        publication_date=pub_date,
                        source_id=category.source_id,
                        category_name=category.name
                    )
                    
                    db.session.add(article)
        
        db.session.commit()

        return jsonify({"message": "Success"})
