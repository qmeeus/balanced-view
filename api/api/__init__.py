import os.path as p

def abspath(relpath):
    return p.abspath(p.join(p.dirname(__file__), relpath))

