from flask import Flask,g
from .config import config
from .extensions import cors,socketio
from app.config import config
from app.models import *
import click
import os
from flask_wtf.csrf import generate_csrf

# Global
PLAYERS = {}

def create_app():
    app = Flask(__name__)
    config_name = os.getenv('FLASK_CONFIG', 'development')
    app.config.from_object(config[config_name])

    register_extensions(app)
    register_commands(app)
    register_blueprints(app)
    register_request(app)

    return app 

def register_extensions(app):
    cors.init_app(app)
    socketio.init_app(app)
    
    socketio.async_mode='threading'
    cors.origins=os.environ.get('CORS_ORIGINS')

def register_commands(app):
    pass

def register_blueprints(app):
    from app.blueprints.home import home_bp
    from app.blueprints.game import game_bp
    from app.blueprints.user import user_bp

    app.register_blueprint(game_bp)
    app.register_blueprint(home_bp)
    app.register_blueprint(user_bp)

def register_request(app):
    @app.before_request
    def set_csrf_token():
        g.csrf_token = generate_csrf()