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

# Optional: Flask-Limiter for rate limiting (install with: pip install flask-limiter)
try:
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address

    limiter = Limiter(
        get_remote_address,
        storage_uri="memory://",
        strategy="fixed-window",
    )
except ImportError:
    limiter = None

# JWT Configuration for cookie-based authentication (Secure Handshake)
# Use both cookies AND headers for redundancy during file uploads
jwt_config = {
    "JWT_TOKEN_LOCATION": ["cookies", "headers"],
    "JWT_ACCESS_TOKEN_HEADER_NAME": "Authorization",
    "JWT_COOKIE_SECURE": False,  # Allow non-secure cookies for localhost
    "JWT_COOKIE_HTTPONLY": True,  # Prevents XSS from accessing tokens
    "JWT_COOKIE_SAMESITE": "Lax",  # CSRF protection
    "JWT_COOKIE_CSRF_PROTECT": False,  # Disabled for development to allow file uploads
}
