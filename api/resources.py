from flask import request, jsonify
from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from datetime import datetime as dt
from time import mktime
import json

from api.utils.patterns import Json
from api.engine.articles import fetch_articles
from api.engine.text import analyse


class NewsArticles(Resource):

    def __init__(self):
        self.parser = RequestParser()
        self.parser.add_argument('query', type=str, required=True)
        self.parser.add_argument('source_language', type=str)
        self.parser.add_argument('languages', type=str)
        self.parser.add_argument('country', type=str)
        self.parser.add_argument('sources', type=str)
        
    def get(self) -> Json:
        params = self.parser.parse_args()
        articles = fetch_articles(params.query, params.language, params.country, params.sources)
        return jsonify(articles)


class TextAnalysis(Resource):

    def __init__(self):
        self.parser = RequestParser()
        self.parser.add_argument('text', type=str, required=True)

    def get(self) -> Json:
        params = self.parser.parse_args()
        analysis = analyse(params.text)
        return jsonify(analysis)
