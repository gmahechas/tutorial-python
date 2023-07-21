from flask import Flask
from routes import init_routes


def create_app() -> Flask:
    application = Flask(__name__)

    with application.app_context():
        init_routes()

    return application
