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

from flask import Flask
from .routes import init_routes

def create_app():

    app = Flask(__name__)
    
    with app.app_context():
        init_routes()

    return app