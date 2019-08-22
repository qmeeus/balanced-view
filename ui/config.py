import os, os.path as p
import dotenv


dotenv.load_dotenv(p.join(p.dirname(__file__), ".env"))


class Base:
    DEBUG = True
    SECRET_KEY = os.environ["SECRET_KEY"]
