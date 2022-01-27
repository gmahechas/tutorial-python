from flask import Blueprint
from .country import country_blueprint

v2_blueprint = Blueprint('v2/3', __name__, url_prefix='/v2/3')


def init_routes_v2():
    v2_blueprint.register_blueprint(country_blueprint)
