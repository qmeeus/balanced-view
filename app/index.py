from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from flask_wtf import FlaskForm
from wtforms import TextField, TextAreaField, validators, StringField, SubmitField
from wtforms.fields.html5 import DateField

import re
from summa import keywords
from .api import fetch_articles, get_keywords


bp = Blueprint('index', __name__, url_prefix='/')
DATE_FORMAT_CHECK = re.compile(r"\d{4}-\d{2}-\d{2}")


class FactForm(FlaskForm):
    text = TextAreaField('Text:', validators=[validators.required()])
    start_date = DateField('From', format='%Y-%m-%d')
    end_date = DateField('To', format='%Y-%m-%d')


@bp.route('/', methods=['POST','GET'])
def fact_checker():
    form = FactForm()
    if form.validate_on_submit():
        text = form.text.data
        start_date = form.start_date.data.strftime('%Y-%m-%d')
        end_date = form.end_date.data.strftime("%Y-%m-%d")
        predictions = get_keywords(text, n_words=5, split=True, scores=True)
        articles = fetch_articles(text, start_date, end_date)
        return render_template('index.html', form=form, query=text, predictions=predictions, search_results=articles)
    return render_template('index.html', form=form, query=0, predictions=0, search_results=0)
