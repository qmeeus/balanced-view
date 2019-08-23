import os, os.path as p
import dotenv


dotenv.load_dotenv(p.join(p.dirname(__file__), ".env"))

class Config(object):
    DEBUG = True
    SECRET_KEY = os.environ["SECRET_KEY"]

    DATABASE = {
        'prefix': os.environ["SQLALCHEMY_DATABASE_PREFIX"],
        'db': p.join(p.dirname(__file__), os.environ["SQLALCHEMY_DATABASE_NAME"]),
    }

    SQLALCHEMY_DATABASE_URI = "{prefix}://{db}".format(**DATABASE)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
