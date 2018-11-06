# from model.keyword_detection import load_model, Config, predict
# from model.keyword_detection import Config, Model
from summa import keywords

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

bp = Blueprint('index', __name__, url_prefix='/')
# model = Model(Config(), load_from_file=True)


@bp.route('/', methods=('GET', 'POST'))
def index():

    if request.method == 'POST':
        text = request.form['text']
        error = None

        if not text:
            error = 'No text found.'

        if error is None:
            # TODO: logic send text to model -> get back results -> search NewsAPI -> render best results
            # predictions = model.predict([text], n)
            predictions = keywords.keywords(text, words=5, split=True, scores=True)
            return render_template('results.html', predictions=predictions)

        flash(error)

    return render_template('index.html')
