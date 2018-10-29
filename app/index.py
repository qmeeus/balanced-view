from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

bp = Blueprint('index', __name__, url_prefix='/')


@bp.route('/', methods=('GET', 'POST'))
def index():
    if request.method == 'POST':
        text = request.form['text']
        error = None

        if not text:
            error = 'No text found.'

        if error is None:
            # TODO: logic send text to model -> get back results -> render
            return text  # redirect(url_for('results'))

        flash(error)

    return render_template('index.html')
