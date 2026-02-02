"""
FarmAT API Routes Package
"""

from app.routes.auth import auth_bp
from app.routes.farmer import farmer_bp
from app.routes.buyer import buyer_bp
from app.routes.admin import admin_bp
from app.routes.payments import payments_bp

__all__ = ["auth_bp", "farmer_bp", "buyer_bp", "admin_bp", "payments_bp"]
