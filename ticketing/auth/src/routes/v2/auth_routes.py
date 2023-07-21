from flask import Blueprint

auth_blueprint = Blueprint('users', __name__, url_prefix='/users')


@auth_blueprint.route('/signup', methods=['GET'])
def signup():
    return 'signup v2'
