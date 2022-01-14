# from flask import Flask, render_template

# app = Flask(__name__)

# @app.route("/me")
# def me():
#     user1 = { "username": "tavogus", "theme": "dark", "image": "image_url" }
#     print(user1)
#     user2 = dict(username="tavogus", theme="dark", image="image_url")
#     print(user2)
#     return {
#         "username": user1["username"],
#         "theme": user1["theme"],
#         "image": user1["image"],
#     }

# @app.route('/hello/<name>')
# def hello(name=None):
#     return render_template('hello.html', name=name)

import os

from flask import Flask


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    # app.config.from_mapping(
    #     SECRET_KEY='dev',
    #     DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    # )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route("/me")
    def me():
        return "Hello, World!"

    return app