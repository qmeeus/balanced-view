#!/usr/bin/env python3

from flask import Flask
from flask_restful import Api
from flask_marshmallow import Marshmallow

# create and configure the app
app = Flask(__name__)

from .config import Production as Config
app.config.from_object(Config())

ma = Marshmallow(app)
api = Api(app)

from . import resources
api.add_resource(resources.NewsArticles, '/articles')
api.add_resource(resources.TextAnalysis, '/analyse')

application = app
