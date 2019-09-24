import os


class Development:
    DEBUG = True
    SECRET_KEY = os.environ["SECRET_KEY"]


class Production(Development):

    DEBUG = False

