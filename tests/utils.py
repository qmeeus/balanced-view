import os.path as p


def load_test_data():
    with open(p.join(p.dirname(__file__), "test_data/texts.txt")) as f:
        raw = f.read()
    yield from filter(lambda txt: len(txt) > 0, map(str.strip, raw.split("\n\n")))

