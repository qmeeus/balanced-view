import os
from flask import Flask


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True, template_folder="ui/templates", static_folder="ui/static") # ,root_path="ui"
    app.config.from_mapping(
        # TODO: adjust to real settings 
        # TODO: include necessary config for heroku including port (localed in env. var. $PORT) 
        SECRET_KEY='dev',
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from .ui import index
    app.register_blueprint(index.bp)

    return app