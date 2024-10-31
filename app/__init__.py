import os

from dotenv import load_dotenv
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
jwt = JWTManager()


def create_app():

    load_dotenv()

    app = Flask(__name__)
    app.config.from_object("config.Config")

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)

    # Register routes here
    from app.routes import api_bp

    app.register_blueprint(api_bp, url_prefix="/api")
    with app.app_context():
        from app import models

    return app
