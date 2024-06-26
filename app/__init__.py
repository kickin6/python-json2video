from flask import Flask
from .config import config
from .routes import main_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(config)
    
    # Register Blueprints
    app.register_blueprint(main_bp)

    return app
