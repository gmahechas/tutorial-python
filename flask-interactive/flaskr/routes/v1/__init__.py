from flask import current_app, Blueprint

v1_blueprint = Blueprint('rest/v1/3', __name__, url_prefix='/rest/v1/3')

from .country import country_blueprint

def init_routes_v1():
    v1_blueprint.register_blueprint(country_blueprint)
    current_app.register_blueprint(v1_blueprint)