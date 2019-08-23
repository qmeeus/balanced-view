import os
import requests
from flask import request, render_template, Blueprint

from .forms import TextForm

bp = Blueprint('index', __name__, url_prefix='/')

@bp.route('/', methods=['POST','GET'])
def index():
    form = TextForm()
    if form.validate_on_submit():
        text = form.text.data
        try:
            url = os.environ["API_URL"]
            data = requests.post(url, data={'text': text}).json()
        except Exception as err:
            error = {"error": {"text": "API is unreachable", "reason": str(err)}}
            data = {"articles": error, "graph": error}
        return render_template('index.html', form=form, search_results=data["articles"], data=data["graph"])
    return render_template('index.html', form=form)
