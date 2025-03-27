# app/__init__.py
from flask import Flask, jsonify
from .routes import app as routes_blueprint

def create_app():
    app = Flask(__name__)
    app.register_blueprint(routes_blueprint)

    @app.route('/')
    def health_check():
        return jsonify({"status": "healthy"}), 200

    return app