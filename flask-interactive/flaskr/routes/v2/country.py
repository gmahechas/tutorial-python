from flask import Blueprint

country_blueprint = Blueprint('country', __name__, url_prefix='/country')


@country_blueprint.route('/create/one', methods=['GET'])
def create_one():
    return 'create/one'


@country_blueprint.route('/update/one', methods=['GET'])
def update_one():
    return 'update/one'


@country_blueprint.route('/delete/one', methods=['GET'])
def delete_one():
    return 'delete/one'


@country_blueprint.route('/search/one', methods=['GET'])
def search_one():
    return 'search/one'


@country_blueprint.route('/search/many', methods=['GET'])
def search_many():
    return 'search/many'
