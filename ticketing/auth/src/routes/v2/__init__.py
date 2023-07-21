from flask import Blueprint
from .auth_routes import auth_blueprint

v2_blueprint = Blueprint('v2', __name__, url_prefix='/v2')
v2_blueprint.register_blueprint(auth_blueprint)
