import os, os.path as p
from flask import Flask


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)

    from .config import Base
    app.config.from_object(Base())

    from . import views
    app.register_blueprint(views.bp)

    return app