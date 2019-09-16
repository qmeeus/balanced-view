import os.path as p
import traceback
import sys
import json


DATA_DIR = p.join(p.dirname(__file__), "test_data")


def load_texts():
    with open(p.join(DATA_DIR, "texts.txt")) as f:
        raw = f.read()
    yield from filter(lambda txt: len(txt) > 0, map(str.strip, raw.split("\n\n")))

def load_rss_sources():
    with open(p.join(DATA_DIR, "rss_sources.json")) as f:
        return json.load(f)


def debug(debugger=False):
    def _debug(func):
        def wrapper(*args):
            print(f"Call {func.__name__}:", *args)
            if debugger:
                import ipdb; ipdb.set_trace()
            retval = func(*args)
            print("Return value:", retval)
            return retval
        return wrapper
    return _debug


def safe(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            traceback.print_exc(file=sys.stdout)
    return wrapper
