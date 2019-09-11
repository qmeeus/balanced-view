import os, os.path as p
import dotenv


dotenv.load_dotenv(p.join(p.dirname(__file__), ".env"))

class Test:
    DEBUG = True
    SECRET_KEY = os.environ["SECRET_KEY"]

    DATABASE = {
        'prefix': 'sqlite',
        'db': 'data/api.db',
    }

    SQLALCHEMY_DATABASE_URI = "{prefix}:///{db}".format(**DATABASE)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class Development(Test):

    DATABASE = {
        'prefix': 'sqlite',
        'db': '/var/lib/sqlite/api.db',
    }

    SQLALCHEMY_DATABASE_URI = "{prefix}:///{db}".format(**DATABASE)


class Production(Development):

    DEBUG = False

    DATABASE = {
        'prefix': os.environ["SQLALCHEMY_DATABASE_PREFIX"],
        'host': os.environ["SQLALCHEMY_DATABASE_HOST"],
        'port': os.environ["SQLALCHEMY_DATABASE_PORT"],
        'user': os.environ["SQLALCHEMY_DATABASE_USER"],
        'pw': os.environ["SQLALCHEMY_DATABASE_PASSWORD"],
        'db': os.environ["SQLALCHEMY_DATABASE_NAME"],

    }

    SQLALCHEMY_DATABASE_URI = "{prefix}://{user}:{pw}@{host}:{port}/{db}".format(**DATABASE)
