"""
App Factory & Extension Initialization

Creates Flask app and initializes extensions:
- SQLAlchemy (database)
- JWT-Extended (authentication)
- CORS (cross-origin requests)
"""

from flask import Flask, request, after_this_request, make_response
from flask_cors import CORS
from app.extensions import db, jwt, migrate, limiter, jwt_config
from app.config import DevelopmentConfig, ProductionConfig, TestingConfig
from app.schemas import ma


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
    
    # Apply JWT config from extensions (ensures both cookies and headers are accepted)
    for key, value in jwt_config.items():
        app.config[key] = value

    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)  # Initialize Flask-Migrate
    ma.init_app(app)  # Initialize Marshmallow
    
    # Configure CORS for credentials
    frontend_url = app.config.get("FRONTEND_URL", "http://localhost:5173")
    CORS(
        app,
        resources={
            r"/api/*": {
                "origin": frontend_url,
                "supports_credentials": True,
                "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
                "expose_headers": ["Set-Cookie", "Authorization"],
                "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
            }
        },
    )
    jwt.init_app(app)
    # Initialize Flask-Limiter if available
    if limiter:
        limiter.init_app(app)

    # Fallback CORS handler for all responses
    @app.after_request
    def add_cors_headers(response):
        origin = request.headers.get(
            "Origin", app.config.get("FRONTEND_URL", "http://localhost:5173")
        )
        if request.path.startswith("/api"):
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Headers"] = (
                "Content-Type, Authorization"
            )
            response.headers["Access-Control-Allow-Methods"] = (
                "GET, POST, PUT, PATCH, DELETE, OPTIONS"
            )
            response.headers["Access-Control-Allow-Credentials"] = "true"
        return response

    # Handle OPTIONS preflight requests
    @app.route("/api/<path:path>", methods=["OPTIONS"])
    def options_handler(path):
        from flask import Response

        return Response(status=200)

    # All operations inside app context
    with app.app_context():
        # Import models to register them with SQLAlchemy
        from app import models

        # Create database tables
        db.create_all()

        # Import and register RESTful API resources (for future use)
        try:
            from app.routes import (
                auth_api,
                farmer_api,
                buyer_api,
                admin_api,
                payments_api,
            )
            # APIs are available but currently using blueprints for backward compatibility
        except ImportError:
            pass

        # Register blueprints for backward compatibility
        from app.routes import (
            auth_bp,
            farmer_bp,
            buyer_bp,
            admin_bp,
            payments_bp,
            api_bp,
        )

        app.register_blueprint(auth_bp, url_prefix="/api/auth")
        app.register_blueprint(farmer_bp, url_prefix="/api/v1/farmer")
        app.register_blueprint(buyer_bp, url_prefix="/api/buyer")
        app.register_blueprint(admin_bp, url_prefix="/api/admin")
        app.register_blueprint(payments_bp, url_prefix="/api/payments")
        app.register_blueprint(api_bp)  # /api/livestock and /api/orders/my_orders

    # Return app and limiter for use in route modules
    app.limiter = limiter

    return app
