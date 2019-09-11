import os, os.path as p
from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow


# create and configure the app
app = Flask(__name__)

from .config import Production as Config
app.config.from_object(Config())

db = SQLAlchemy(app)
ma = Marshmallow(app)
api = Api(app)

from . import resources
api.add_resource(resources.BalancedView, '/')
api.add_resource(resources.DataFetcher, '/update')


if __name__ == '__main__':
    app.run(debug=True)
