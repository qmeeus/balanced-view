from marshmallow import fields, pre_load, validate
from api.wsgi import ma


class GroupSchema(ma.Schema):
    name = fields.String(required=True)
    value = fields.String(required=True)


class GroupByOptions(ma.Schema):
    key = fields.String(required=True)
    default = fields.String(required=False)
    groups = fields.List(fields.Nested(GroupSchema), required=True)


class SourceOptions(ma.Schema):
    name = fields.String(required=False)
    id = fields.String(required=False)
    categories = fields.List(fields.String(), required=False)


class DefaultOptions(ma.Schema):
    output_language = fields.String(required=False)
    search_languages = fields.List(fields.String(), required=False)
    categories = fields.Nested(GroupByOptions, required=False)

class AnalysisOptions(DefaultOptions):
    input_text = fields.String(required=True)
    related = fields.Boolean(required=False)

class ArticlesOptions(DefaultOptions):
    terms = fields.List(fields.String(), required=True)
    source_language = fields.String(required=True)
