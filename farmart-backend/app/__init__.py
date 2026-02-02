"""
App Factory & Extension Initialization

Creates Flask app and initializes extensions:
- SQLAlchemy (database)
- JWT-Extended (authentication)
- CORS (cross-origin requests)
"""

from flask import Flask
from flask_cors import CORS
from app.extensions import db, jwt
from app.config import DevelopmentConfig, ProductionConfig, TestingConfig


def create_app(config_name="development"):
    """
    Application factory for creating Flask app instance.

    Args:
        config_name: Configuration environment ('development', 'production', 'testing')

    Returns:
        Configured Flask application
    """
    app = Flask(__name__)

    # Load configuration
    config_map = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
        "testing": TestingConfig,
        "default": DevelopmentConfig,
    }
    app.config.from_object(config_map.get(config_name, DevelopmentConfig)())

    # Initialize extensions with app
    db.init_app(app)
    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": app.config.get("FRONTEND_URL", "http://localhost:5173")
            }
        },
    )
    jwt.init_app(app)

    # All operations inside app context
    with app.app_context():
        # Import models to register them with SQLAlchemy
        from app import models

        # Create database tables
        db.create_all()

        # Import and register blueprints
        from app.routes import auth_bp, farmer_bp, buyer_bp, admin_bp, payments_bp

        app.register_blueprint(auth_bp, url_prefix="/api/auth")
        app.register_blueprint(farmer_bp, url_prefix="/api/farmer")
        app.register_blueprint(buyer_bp, url_prefix="/api/buyer")
        app.register_blueprint(admin_bp, url_prefix="/api/admin")
        app.register_blueprint(payments_bp, url_prefix="/api/payments")

    return app
