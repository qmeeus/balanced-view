import os, os.path as p
from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_talisman import Talisman


# create and configure the app
app = Flask(__name__)

from .config import Config
app.config.from_object(Config())

talisman = Talisman(app, force_https=False)

db = SQLAlchemy(app)
api = Api(app)

from . import resources
api.add_resource(resources.BalancedView, '/')


if __name__ == '__main__':
    app.run(debug=True)
