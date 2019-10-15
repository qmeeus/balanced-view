import os
import requests
from flask import request, render_template, Blueprint, flash
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

            url = os.environ["API_URL"] + "/analyse"
            opts = {
                'input_text': text, 
                'related': True,
                'search_languages': ['en', 'fr', 'nl'],
                'groupby_options': {
                    'key': 'language',
                    'default': 'Other languages',
                    'groups': [
                        {'name': 'Dutch', 'value': 'nl'},
                        {'name': 'French', 'value': 'fr'}
                    ],
                    'orderby': 'relevance',
                    'reverse': False,
                    'max_results_per_group': 5
                }
            }
            resp = requests.post(url, json=opts)
            data = resp.json()
            logger.debug(data)
            error_message = ""

            if "message" in data:
                error_message = data["message"]

        except Exception as err:
            logger.exception(err)
            error_message = "The backend server is unreachable"

        if not error_message:
            articles, graph = data["articles"], data["graph"]
            return render_template('results.html', form=form, articles=articles, graph=graph)

        flash(error_message, "error")

    return render_template('index.html', form=form)
