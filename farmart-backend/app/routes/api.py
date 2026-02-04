"""
Public API Routes
Provides public endpoints for livestock listings and orders
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Livestock, Order, User
from app import db

# Create a new blueprint with /api prefix
api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/livestock", methods=["GET"])
def get_livestock():
    """
    Get all available livestock for sale.
    Public endpoint for the marketplace.
    """
    # Get query parameters for filtering
    species = request.args.get("species")
    min_price = request.args.get("minPrice", type=float)
    max_price = request.args.get("maxPrice", type=float)
    location = request.args.get("location")
    sort_by = request.args.get("sortBy", "newest")

    # Filter by is_available = True
    query = Livestock.query.filter_by(is_available=True)

    if species:
        query = query.filter(Livestock.animal_type.ilike(f"%{species}%"))
    if min_price:
        query = query.filter(Livestock.price >= min_price)
    if max_price:
        query = query.filter(Livestock.price <= max_price)
    if location:
        query = query.filter(Livestock.location.ilike(f"%{location}%"))

    # Sort options
    if sort_by == "price-low":
        query = query.order_by(Livestock.price.asc())
    elif sort_by == "price-high":
        query = query.order_by(Livestock.price.desc())
    else:
        query = query.order_by(Livestock.created_at.desc())

    livestock = query.all()

    return jsonify([
        {
            "id": item.id,
            "name": item.animal_type,  # Use animal_type as name
            "species": item.animal_type,
            "breed": item.breed,
            "price": float(item.price),
            "location": item.location,
            "images": [],
            "weight": item.weight,
            "age_months": item.age_months,
        }
        for item in livestock
    ]), 200


@api_bp.route("/orders/my_orders", methods=["GET"])
@jwt_required()
def get_my_orders():
    """
    Get current user's orders.
    """
    current_user_id = get_jwt_identity()

    orders = (
        Order.query
        .filter_by(buyer_id=current_user_id)
        .order_by(Order.created_at.desc())
        .all()
    )

    return jsonify([
        {
            "id": order.id,
            "order_number": order.order_number,
            "livestock": {
                "id": order.livestock.id,
                "name": order.livestock.animal_type,
                "species": order.livestock.animal_type,
            }
            if order.livestock
            else None,
            "total_amount": float(order.total_amount),
            "status": order.status,
            "created_at": order.created_at.isoformat() if order.created_at else None,
        }
        for order in orders
    ]), 200
