from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.utils.validators import OrderCreateSchema, validate_request

buyer_bp = Blueprint("buyer", __name__, url_prefix="/api/buyer")


@buyer_bp.route("/ping", methods=["GET"])
def buyer_ping():
    """
    Health check for buyer routes
    """
    return jsonify({
        "status": "success",
        "message": "Buyer routes are working 🚀"
    }), 200


@buyer_bp.route("/orders", methods=["POST"])
@jwt_required()
def create_order():
    """
    Create a new order (mock implementation)
    """
    user_id = get_jwt_identity()
    data = request.get_json()

    validated = validate_request(OrderCreateSchema(), data)

    return jsonify({
        "status": "success",
        "message": "Order created successfully",
        "buyer_id": user_id,
        "order": validated
    }), 201


@buyer_bp.route("/orders", methods=["GET"])
@jwt_required()
def my_orders():
    """
    Get buyer orders (mock data)
    """
    user_id = get_jwt_identity()

    return jsonify({
        "status": "success",
        "buyer_id": user_id,
        "orders": []
    }), 200
