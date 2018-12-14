from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from flask_wtf import FlaskForm
from wtforms import TextAreaField, validators
import json

from .api import fetch_articles, get_graph


bp = Blueprint('index', __name__, url_prefix='/')

class FactForm(FlaskForm):
    text = TextAreaField('Text:', validators=[validators.required()])

    def validate(self):
        if not self.text.validate(self):
            return False
        return True


@bp.route('/', methods=['POST','GET'])
def fact_checker():
    form = FactForm()
    if form.validate_on_submit():
        text = form.text.data
        articles = fetch_articles(text)
        return render_template('index.html', form=form, search_results=articles)
    return render_template('index.html', form=form)

@bp.route('/graph', methods=["GET"])
def graph():
    text = """The Mueller Witch Hunt is a total disgrace. They are looking at supposedly stolen Crooked 
    Hillary Clinton Emails (even though they don’t want to look at the DNC Server), but have no interest 
    in the Emails that Hillary DELETED & acid washed AFTER getting a Congressional Subpoena!"""
    graph_data = get_graph(text)
    return render_template('graph.html', data=graph_data)