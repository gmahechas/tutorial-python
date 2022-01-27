from flask import Blueprint

estate_blueprint = Blueprint('estate', __name__, url_prefix='/estate')


@estate_blueprint.route('/create/one', methods=['GET'])
def create_one():
    return 'create/one'


@estate_blueprint.route('/update/one', methods=['GET'])
def update_one():
    return 'update/one'


@estate_blueprint.route('/delete/one', methods=['GET'])
def delete_one():
    return 'delete/one'


@estate_blueprint.route('/search/one', methods=['GET'])
def search_one():
    return 'search/one'


@estate_blueprint.route('/search/many', methods=['GET'])
def search_many():
    return 'search/many'
