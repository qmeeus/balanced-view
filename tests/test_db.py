import json
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields, pprint

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'super-secret'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    url = db.Column(db.String(200), nullable=False)
    id_source = db.Column(db.ForeignKey('source.id'))

class Source(db.Model):
    id = db.Column(db.String(80), primary_key=True)
    name = db.Column(db.String(80))
    lang = db.Column(db.String(10))
    country = db.Column(db.String(20))
    url = db.Column(db.String(200))
    origin = db.Column(db.String(3), default="api")
    categories = db.relationship("Category", backref="category")

class CategorySchema(Schema):
    class Meta:
        model = Category
        fields = ("name", "url")

class SourceSchema(Schema):
    class Meta:
        model = Source
        fields = ("id", "name", "lang", "country", "url", "origin", "categories")

    categories = fields.List(fields.Nested(CategorySchema))

category_schema = CategorySchema()
source_schema = SourceSchema()

categories_schema = CategorySchema(many=True)
sources_schema = SourceSchema(many=True)

@app.route('/')
def index():
    return "<a href='/dump_category'>Dump Categories</a><br><a href='/dump_source'>Dump Sources</a>"

@app.route('/dump_category')
def dump_category():
    category = Category.query.all()
    return jsonify(categories_schema.dump(category))

@app.route('/dump_source')
def dump_source():
    source = Source.query.all()
    return jsonify(sources_schema.dump(source))


def build_db():
    db.drop_all()
    db.create_all()
    
    sample_file = "rss_sources.json"
    with open(sample_file) as json_file:
        sample_data = json.load(json_file)

    for source_json in sample_data["sources"]:
        categories = source_json.pop("categories")
        source = Source(**source_json)
        db.session.add(source)
        for category_json in categories:
            category = Category(id_source=source.id, **category_json)
            db.session.add(category)

    db.session.commit()


@app.before_first_request
def first_request():
    build_db()

if __name__ == '__main__':
    app.run(debug=True, port=7777)