from flask import Blueprint

country_blueprint = Blueprint('country', __name__, url_prefix='/country')


@country_blueprint.route('/create', methods=['GET'])
def signup():
    return 'create country'
