from flask import request, jsonify
from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from datetime import datetime as dt
from time import mktime
import json

from api.engine.articles import fetch_articles
from api.engine.text import TextAnalyser
from api.utils.schemas import AnalysisOptions, ArticlesOptions
from api.utils.logger import logger
from api.utils.patterns import Json
from api.utils.exceptions import (
    NLPModelNotFound, BackendError, TextRankError, TranslationError, 
    MalformedJSONException, EmptyJSONException
)


class Meta(Resource):

    def __init__(self) -> None:
        self.schema = None
        raise NotImplementedError

    def get_opts(self):
        json_data = request.get_json(force=True)
        if not json_data:
            raise EmptyJSONException("No data provided")
        try:
            return self.schema.load(json_data)
        except Exception as err:
            logger.exception(err)
            raise MalformedJSONException("Wrong parameters passed")

    @staticmethod
    def _get_message(exception):

        if isinstance(exception, EmptyJSONException):
            message = "No input data provided"
        elif isinstance(exception, MalformedJSONException):
            message = "Malformed JSON"
        elif isinstance(exception, BackendError):
            message = "Backend is not available"
        elif isinstance(exception, TranslationError):
            message = "The text could not be translated"
        elif isinstance(exception, TextRankError):
            message = "No keywords extracted for searching"
        elif isinstance(exception, NLPModelNotFound):
            message = "This language is not supported at the moment"
        else:
            message = "An unexpected error occured"
        return jsonify({"message": message})


class NewsArticles(Meta):

    def __init__(self) -> None:
        self.schema = ArticlesOptions()
        
    def post(self) -> Json:
        try:
            options = self.get_opts()
            return jsonify(fetch_articles(**self.schema.dump(options)))

        except Exception as err:
            logger.exception(err)
            return self._get_message(err)


class TextAnalysis(Meta):

    def __init__(self) -> None:
        self.schema = AnalysisOptions()

    def post(self) -> Json:

        try:
            options_dict = self.schema.dump(self.get_opts())
            input_text = options_dict.pop("input_text")
            return jsonify(TextAnalyser(**options_dict).fit(input_text).to_dict())

        except Exception as err:
            logger.exception(err)
            return self._get_message(err)

