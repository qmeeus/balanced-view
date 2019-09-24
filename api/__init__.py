import os.path as p
import dotenv


def abspath(relpath):
    return p.abspath(p.join(p.dirname(__file__), relpath))


dotenv.load_dotenv(abspath(".env"))

