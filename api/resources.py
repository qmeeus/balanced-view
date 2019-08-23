from flask_restful import Resource, reqparse
from hashlib import md5
import datetime as dt
from . import balancedview
from .models import Keyword, InputText, Article, Source
from .api import db

DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

parser = reqparse.RequestParser()
parser.add_argument('text')

class BalancedView(Resource):

    def post(self):
        params = parser.parse_args()
        output = balancedview.run(params)
        text = InputText(
            id=md5(params["text"].encode()).hexdigest(), 
            text=params["text"], 
            timestamp=dt.datetime.now(), 
            detected_language=output["language"])

        if output["keywords"]:
            for kwd_val in output["keywords"]:
                kwd = db.session.query(Keyword).filter_by(value=kwd_val).first()
                if not kwd:
                    kwd = Keyword(value=kwd_val)
                    db.session.add(kwd)
                text.keywords.append(kwd)

        if "error" not in output["articles"]:
            text.totalResults=output["totalResults"]
            for articles_collection in output["articles"].values():
                for result in articles_collection:
                    article = db.session.query(Article).filter_by(
                        title=result["title"], publication_date=result["publishedAt"]).first()
                    if not article:
                        source = db.session.query(Source).get(result["source"]["id"])
                        if not source:
                            source = Source(
                                id=result["source"]["id"], 
                                name=result["source"]["name"])
                            db.session.add(source)
                        
                        article = Article(
                            title=result["title"],
                            articleURL=result["url"],
                            author=result["author"],
                            description=result["description"],
                            imageURL=result["urlToImage"],
                            publication_date=dt.datetime.strptime(result["publishedAt"], DATE_FORMAT),
                            idSource=source.id)
                        db.session.add(article)

                    text.articles.append(article)

        db.session.add(text)
        db.session.commit()
                            
        return output
