from flask import Flask
from flask_restful import Resource, Api, reqparse
import balancedview_api

# Instantiate the app
app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('text')

class BalancedView(Resource):
    def post(self):
        params = parser.parse_args()
        return balancedview_api.run(params)

# Create routes
api.add_resource(BalancedView, '/')

# Run the application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
