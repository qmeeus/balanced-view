from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from flask_wtf import FlaskForm
from wtforms import TextAreaField, validators
import json

from .api import balancedview_api 


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
        data = balancedview_api.run({'text': text, 'language': 'en'})
        return render_template('index.html', form=form, search_results=data["articles"], data=data["graph"])
    return render_template('index.html', form=form)


# @bp.route('/translate', methods=['POST', 'GET'])
# def translate():
#     form = FactForm()
#     if form.validate_on_submit():
#         text = form.text.data
#         translation = IBMTranslator()(text)
#         print(translation)
#     return render_template('index.html', form=form)