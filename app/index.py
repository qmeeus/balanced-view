from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from flask_wtf import FlaskForm
from wtforms import TextField, TextAreaField, validators, StringField, SubmitField
from wtforms.fields.html5 import DateField
from wtforms_components import DateRange
from datetime import date
from dateutil.relativedelta import relativedelta

from summa import keywords
from .api import fetch_articles, get_keywords


bp = Blueprint('index', __name__, url_prefix='/')

class FactForm(FlaskForm):
    text = TextAreaField('Text:', validators=[validators.required()])
    start_date = DateField('From', format='%Y-%m-%d', 
        validators=[DateRange(min=date.today() + relativedelta(months=-1), max=date.today())])
    end_date = DateField('To', format='%Y-%m-%d', validators=[DateRange(max=date.today())])


@bp.route('/', methods=['POST','GET'])
def fact_checker():
    form = FactForm()
    if form.validate_on_submit():
        text = form.text.data
        start_date = form.start_date.data.strftime('%Y-%m-%d') if form.start_date else None
        end_date = form.end_date.data.strftime("%Y-%m-%d") if form.end_date else None
        articles = fetch_articles(text, start_date, end_date)
        print(form.errors)
        return render_template('index.html', form=form, search_results=articles)
    return render_template('index.html', form=form)
