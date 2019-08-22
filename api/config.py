import os, os.path as p
import dotenv


dotenv.load_dotenv(p.join(p.dirname(__file__), ".env"))

class Config(object):
    DEBUG = True
    SECRET_KEY = os.environ["SECRET_KEY"]

    POSTGRES = {
        'user': os.environ["POSTGRES_USER"],
        'pw': os.environ["POSTGRES_PASSWORD"],
        'db': os.environ["POSTGRES_DB"],
        'host': os.environ["POSTGRES_HOST"],
        'port': os.environ["POSTGRES_PORT"],
    }

    SQLALCHEMY_DATABASE_URI = "postgresql://{user}:{pw}@{host}:{port}/{db}".format(**POSTGRES)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
