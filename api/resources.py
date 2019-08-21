from flask_restful import Resource, reqparse
from . import balancedview


parser = reqparse.RequestParser()
parser.add_argument('text')

class BalancedView(Resource):
    def post(self):
        params = parser.parse_args()
        return balancedview.run(params)
