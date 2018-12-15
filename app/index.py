from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from flask_wtf import FlaskForm
from wtforms import TextAreaField, validators
import json

from .api.fakenewsapi import FakeNewsAPI


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
        fakenewsapi = FakeNewsAPI(text)
        articles = fakenewsapi.get_results()
        graph_data = fakenewsapi.get_graph()
        return render_template('index.html', form=form, search_results=articles, data=graph_data)
    return render_template('index.html', form=form)
