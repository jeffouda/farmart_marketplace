"""
FarmAT API Routes Package
Exports both blueprints (for backward compatibility) and RESTful APIs
"""

# Import blueprints (for backward compatibility)
from app.routes.auth import auth_bp
from app.routes.farmer import farmer_bp
from app.routes.buyer import buyer_bp
from app.routes.admin import admin_bp
from app.routes.payments import payments_bp
from app.routes.api import api_bp

# Import RESTful API objects
from app.routes.auth import auth_api
# Note: Other route files will be refactored to flask-restful

__all__ = [
    "auth_bp",
    "farmer_bp",
    "buyer_bp",
    "admin_bp",
    "payments_bp",
    "api_bp",
    "auth_api",
]
