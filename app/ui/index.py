import requests
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from flask_wtf import FlaskForm
from wtforms import TextAreaField, validators

try:
    from app.api import balancedview_api
except ImportError:
    class Client:
        # QUICKFIX
        # TODO: catch error if request fails
        url = "http://webservice:5000"
        def run(self, params):
            return requests.post(self.url, data=params).json()
    
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
        try:
            data = balancedview_api.run({'text': text})
        except requests.exceptions.ConnectionError:
            error = {"error": {"text": "API is unreachable", "reason": "It might be down or misconfigured"}}
            data = {"articles": error, "graph": error}
        return render_template('index.html', form=form, search_results=data["articles"], data=data["graph"])
    return render_template('index.html', form=form)


if __name__ == "__main__":
    from flask import Flask
    app = Flask(__name__)
    app.config.from_mapping(SECRET_KEY='dev')
    app.register_blueprint(bp)
    app.run(host='0.0.0.0', port=5000, debug=True)