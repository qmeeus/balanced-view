from flask import request, jsonify
from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from datetime import datetime as dt
from time import mktime
import json
from elasticsearch.exceptions import ConnectionError

from api.utils.logger import logger
from api.utils.patterns import Json
from api.engine.articles import fetch_articles
from api.engine.text import TextAnalyser


class NewsArticles(Resource):

    def __init__(self) -> None:
        self.parser = RequestParser()
        self.parser.add_argument('query', type=str, required=True)
        self.parser.add_argument('source_language', type=str)
        self.parser.add_argument('languages', type=str)
        self.parser.add_argument('country', type=str)
        self.parser.add_argument('sources', type=str)
        
    def post(self) -> Json:
        params = self.parser.parse_args()
        try:
            
            articles = fetch_articles(
                params.query, 
                params.source_language,
                params.languages, 
                params.country, 
                params.sources
            )

        except ConnectionError as err:
            
            logger.error(err)
            return jsonify({"error": "Backend is not available"})

        return jsonify(articles)


class TextAnalysis(Resource):

    def __init__(self) -> None:
        self.parser = RequestParser()
        self.parser.add_argument('text', type=str, required=True)
        self.parser.add_argument("related", type=bool)
        self.parser.add_argument('output_language', type=str)
        self.parser.add_argument('article_languages', type=str)

    def post(self) -> Json:
        params = self.parser.parse_args()
        
        analysis = (
            TextAnalyser(
                related_articles=params.related,
                output_language=params.output_language, 
                article_languages=params.article_languages)
            .fit(params.text)
            .to_dict()
        )

        return jsonify(analysis)
