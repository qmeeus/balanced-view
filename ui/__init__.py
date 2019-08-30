import os, os.path as p
from flask import Flask
from flask_talisman import Talisman


def create_app(development=False):
    # create and configure the app
    app = Flask(__name__)

    if development:
        from .config import Development as Config
    else:
        from .config import Production as Config

    app.config.from_object(Config())

    Talisman(app, force_https=False, content_security_policy={'default-src':"'none'",'script-src':"'self'"})

    from . import views
    app.register_blueprint(views.bp)

    return app
