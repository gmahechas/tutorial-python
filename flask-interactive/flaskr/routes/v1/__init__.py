from flask import Blueprint
from .country import country_blueprint
from .estate import estate_blueprint

v1_blueprint = Blueprint('v1/3', __name__, url_prefix='/v1/3')


def init_routes_v1():
    v1_blueprint.register_blueprint(country_blueprint)
    v1_blueprint.register_blueprint(estate_blueprint)
