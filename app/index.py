from model.keyword_detection import load_model, Config, predict

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

bp = Blueprint('index', __name__, url_prefix='/')
model = load_model("model/" + Config().model_file)


@bp.route('/', methods=('GET', 'POST'))
def index():
    if request.method == 'POST':
        text = request.form['text']
        error = None

        if not text:
            error = 'No text found.'

        if error is None:
            # TODO: logic send text to model -> get back results -> render
            predictions = predict(model, [text])
            return predictions.to_html()  # redirect(url_for('results'))

        flash(error)

    return render_template('index.html')
