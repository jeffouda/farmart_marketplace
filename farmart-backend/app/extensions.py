"""
Flask Extensions
Creates extension instances to be used throughout the application
"""

from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()

# JWT Configuration for API tokens
jwt_config = {
    "JWT_TOKEN_LOCATION": ["headers"],
    "JWT_HEADER_NAME": "Authorization",
    "JWT_HEADER_TYPE": "Bearer",
    "JWT_COOKIE_CSRF_PROTECT": False,
}
