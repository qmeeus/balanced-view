from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from flask_wtf import FlaskForm
from wtforms import TextAreaField, validators

try:
    from app.api import balancedview_api
except ImportError:
    import requests
    class Client:
        url = "http://localhost:5001"
        def run(self, params):
            return requests.post(self.url, data=params)
    
    balancedview_api = Client()



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
        data = balancedview_api.run({'text': text})
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

if __name__ == "__main__":
    from flask import Flask
    app = Flask(__name__)
    app.run(host='0.0.0.0', port=5000, debug=True)