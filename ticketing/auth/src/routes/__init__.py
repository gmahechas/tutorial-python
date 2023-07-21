from flask import Blueprint, current_app
from routes.v1 import v1_blueprint
from routes.v2 import v2_blueprint

rest_blueprint = Blueprint('rest', __name__, url_prefix='/rest')


def init_routes():
    rest_blueprint.register_blueprint(v1_blueprint)
    rest_blueprint.register_blueprint(v2_blueprint)
    current_app.register_blueprint(rest_blueprint)
