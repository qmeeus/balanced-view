import os, os.path as p
import dotenv


dotenv.load_dotenv(p.join(p.dirname(__file__), ".env"))

class Config(object):
    DEBUG = True
    SECRET_KEY = os.environ["SECRET_KEY"]
    SERVER_NAME = f"0.0.0.0:{os.environ['FLASK_RUN_PORT']}"

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False