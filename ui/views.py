import os
import requests
from flask import request, render_template, Blueprint
from flask_csp.csp import csp_header

from .forms import TextForm
from .utils.logger import logger

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
            resp = requests.post(url, json={'text': text})
            data = resp.json()
            logger.debug(data)
        except Exception as err:
            error = {"error": {"text": "Houston we have a problem!", "reason": "API is unreachable"}}
            data = {"articles": error, "graph": error}
        return render_template('results.html', form=form, search_results=data["articles"], data=data["graph"])
    return render_template('index.html', form=form)
