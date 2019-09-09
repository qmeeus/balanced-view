import os
import requests
from flask import request, render_template, Blueprint
from flask_csp.csp import csp_header

from .forms import TextForm

bp = Blueprint('index', __name__, url_prefix='/')

content_security_policy = {
    'default-src':"'self' https://stackpath.bootstrapcdn.com https://fonts.gstatic.com",
    'script-src':"'self' https://code.jquery.com https://cdnjs.cloudflare.com https://stackpath.bootstrapcdn.com",
    'style-src': "'self' https://stackpath.bootstrapcdn.com https://fonts.googleapis.com",
    'img-src': "*"
}


@bp.route('/', methods=['POST','GET'])
@csp_header(content_security_policy)
def index():
    form = TextForm()
    if form.validate_on_submit():
        text = form.text.data
        try:
            url = os.environ["API_URL"]
            resp = requests.post(url, data={'text': text})
            data = resp.json()
        except Exception as err:
            error = {"error": {"text": "API is unreachable", "reason": str(err)}}
            data = {"articles": error, "graph": error}
        return render_template('results.html', form=form, search_results=data["articles"], data=data["graph"])
    return render_template('index.html', form=form)
