"""
App Factory & Extension Initialization

Creates Flask app and initializes extensions:
- SQLAlchemy (database)
- JWT-Extended (authentication)
- CORS (cross-origin requests)
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from .config import config_by_name


db = SQLAlchemy()
jwt = JWTManager()


def create_app(config_name="development"):
    """
    Application factory for creating Flask app instance.

    Args:
        config_name: Configuration environment ('development', 'production', 'testing')

    Returns:
        Configured Flask application
    """
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # Initialize extensions
    db.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": app.config["FRONTEND_URL"]}})
    jwt.init_app(app)

    # Register blueprints
    from .routes import auth_bp, farmer_bp, buyer_bp, admin_bp, payments_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(farmer_bp, url_prefix="/api/farmer")
    app.register_blueprint(buyer_bp, url_prefix="/api/buyer")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(payments_bp, url_prefix="/api/payments")

    # Create database tables
    with app.app_context():
        db.create_all()

    return app
