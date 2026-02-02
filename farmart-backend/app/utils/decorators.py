"""
Decorators
@farmer_required, @admin_required logic
"""

from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.models import User


def farmer_required(f):
    """Decorator to require farmer role."""

    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return jsonify({"error": "User not found"}), 404

        if user.role != "farmer":
            return jsonify({"error": "Farmer access required"}), 403

        if not user.is_active:
            return jsonify({"error": "Account is deactivated"}), 403

        return f(*args, **kwargs)

    return decorated_function


def buyer_required(f):
    """Decorator to require buyer role."""

    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return jsonify({"error": "User not found"}), 404

        if user.role != "buyer":
            return jsonify({"error": "Buyer access required"}), 403

        if not user.is_active:
            return jsonify({"error": "Account is deactivated"}), 403

        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    """Decorator to require admin role."""

    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return jsonify({"error": "User not found"}), 404

        if user.role != "admin":
            return jsonify({"error": "Admin access required"}), 403

        if not user.is_active:
            return jsonify({"error": "Account is deactivated"}), 403

        return f(*args, **kwargs)

    return decorated_function
