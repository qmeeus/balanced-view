from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, backref

from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.collections import attribute_mapped_collection

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(64))

    # association proxy of "user_keywords" collection
    # to "keyword" attribute
    keywords = association_proxy('user_keywords', 'keyword')

    def __init__(self, name):
        self.name = name

class UserKeyword(Base):
    __tablename__ = 'user_keyword'
    user_id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    keyword_id = Column(Integer, ForeignKey('keyword.id'), primary_key=True)
    keyword = Column(String(64))
    special_key = Column(String(50))

    # bidirectional attribute/collection of "user"/"user_keywords"
    user = relationship(User, backref=backref(
        "user_keywords",
        collection_class=attribute_mapped_collection("keyword"),
        cascade="all, delete-orphan")
    )

    # reference to the "Keyword" object
    keyword = relationship("Keyword")

    def __init__(self, keyword=None, user=None, special_key=None):
        self.user = user
        self.keyword = keyword
        self.special_key = special_key

class Keyword(Base):
    __tablename__ = 'keyword'
    id = Column(Integer, primary_key=True)
    keyword = Column('keyword', String(64))

    def __init__(self, keyword):
        self.keyword = keyword

    def __repr__(self):
        return 'Keyword(%s)' % repr(self.keyword)


if __name__ == '__main__':
    import ipdb; ipdb.set_trace()

    user = User('log')
    for kw in (Keyword('new_from_blammo'), Keyword('its_big')):
        user.keywords.append(kw)

    print(user.keywords)
    # [Keyword('new_from_blammo'), Keyword('its_big')]