from flask import current_app, Blueprint
from .v1 import v1_blueprint, init_routes_v1
from .v2 import v2_blueprint, init_routes_v2

main_blueprint = Blueprint('rest', __name__, url_prefix='/rest')


def init_routes():
    main_blueprint.register_blueprint(v1_blueprint)
    init_routes_v1()
    main_blueprint.register_blueprint(v2_blueprint)
    init_routes_v2()
    current_app.register_blueprint(main_blueprint)
