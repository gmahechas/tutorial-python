from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from flask_jwt import JWT, jwt_required

from auth.security import authenticate, identity

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'super-secret'

api = Api(app)

jwt = JWT(app, authenticate, identity)  # new endpoint /auth

items = []


class Item(Resource):
    @jwt_required()
    def get(self, name):
        item = next(filter(lambda x: x['name'] == name, items), None)
        return {'item': item}, 200 if item else 404

    def post(self, name):
        if next(filter(lambda x: x['name'] == name, items), None):
            return {'message': 'already exist'}, 400
        request_data = request.get_json()
        items.append(request_data)
        return request_data, 201


class ItemList(Resource):
    def get(self):
        return {'items': items}


api.add_resource(Item, '/item/<string:name>')
api.add_resource(ItemList, '/items')