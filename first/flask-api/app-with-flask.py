from flask import Flask, jsonify, request

app = Flask(__name__)

stores = [{'name': 'Store 1', 'items': [{'name': 'item 1', 'price': 15.99}]}]


@app.route('/store', methods=['POST'])
def create_store():
    request_data = request.get_json()
    new_store = {'name': request_data['name'], 'items': []}
    stores.append(new_store)
    return jsonify(stores)


@app.route('/store/<string:name>')
def get_store(name):
    for store in stores:
        if store['name'] == name:
            return store
    return jsonify({'message': 'not found'})


@app.route('/store')
def get_stores():
    return jsonify({'data': stores})


@app.route('/store/<string:name>/item', methods=['POST'])
def create_item_in_store(name):
    request_data = request.get_json()
    for store in stores:
        if store['name'] == name:
            store['items'].append(request_data)
            return jsonify({'data': request_data})
    return jsonify({'message': 'not found'})


"""     
            store['name']['items'].append(request_data) """


@app.route('/store/<string:name>/item')
def get_item_in_store(name):
    for store in stores:
        if store['name'] == name:
            return jsonify({'items': store['items']})
    return jsonify({'message': 'not found'})
