from flask import Blueprint
from routes.v1.auth_routes import auth_blueprint
from routes.v1.country_routes import country_blueprint

v1_blueprint = Blueprint('v1', __name__, url_prefix='/v1')
v1_blueprint.register_blueprint(auth_blueprint)
v1_blueprint.register_blueprint(country_blueprint)
