import os, os.path as p
from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy


# create and configure the app
app = Flask(__name__)

from .config import Config
app.config.from_object(Config())

db = SQLAlchemy(app)
api = Api(app)

from . import resources
api.add_resource(resources.BalancedView, '/')


if __name__ == '__main__':
    app.run(debug=True)