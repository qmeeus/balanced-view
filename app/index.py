# from model.keyword_detection import load_model, Config, predict
# from model.keyword_detection import Config, Model
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

import re
from summa import keywords
from .api import fetch_articles


bp = Blueprint('index', __name__, url_prefix='/')
DATE_FORMAT_CHECK = re.compile(r"\d{4}-\d{2}-\d{2}")

@bp.route('/', methods=('GET', 'POST'))
def index():

    if request.method == 'POST':
        text = request.form['text']
        # start_date = request.form['start_date']
        # end_date = request.form['end_date']
        error = None

        if not text:
            error = 'No text found.'

        # for date in (start_date, end_date):
        #     if DATE_FORMAT_CHECK.match(date):
        #         error = "Wrong date format. Required format: YYYY-MM-DD"

        if error is None:
            # TODO: logic send text to model -> get back results -> search NewsAPI -> render best results
            # predictions = model.predict([text], n)
            predictions = keywords.keywords(text, words=5, split=True, scores=True)
            # results = fetch_articles(text, start_date, end_date)
            results = fetch_articles(text)
            return render_template('results.html', predictions=predictions, articles=results)

        flash(error)

    return render_template('index.html')
