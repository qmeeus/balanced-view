

def member(it):
    def _member(x):
        return x in it
    return _member

def member_item(it, item):
    def _member(x):
        return x[item] in it
    return _member

def member_attr(it, attr):
    def _member(x):
        return getattr(x, attr) in it
    return _member