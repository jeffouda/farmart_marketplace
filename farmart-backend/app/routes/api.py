"""
Public API Routes
Provides public endpoints for livestock listings and orders
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Livestock, Order, User, Vaccination
from app import db
from datetime import datetime

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
            "name": item.animal_type,
            "species": item.animal_type,
            "breed": item.breed,
            "price": float(item.price),
            "location": item.location,
            "image_url": item.image_url,
            "images": [item.image_url] if item.image_url else [],
            "weight": item.weight,
            "age_months": item.age_months,
            "farmer": {
                "id": item.farmer.id,
                "first_name": item.farmer.first_name,
                "last_name": item.farmer.last_name,
                "farm_name": getattr(item.farmer, "farm_name", None),
            }
            if item.farmer
            else None,
        }
        for item in livestock
    ]), 200


@api_bp.route("/livestock/<int:id>", methods=["GET"])
def get_livestock_by_id(id):
    """
    Get a specific livestock by ID.
    Public endpoint for animal details page.
    """
    livestock = Livestock.query.filter_by(id=id, is_available=True).first()

    if not livestock:
        return jsonify({"error": "Livestock not found"}), 404

    return jsonify({
        "id": livestock.id,
        "name": livestock.animal_type,
        "species": livestock.animal_type,
        "breed": livestock.breed,
        "price": float(livestock.price),
        "location": livestock.location,
        "image_url": livestock.image_url,
        "images": [livestock.image_url] if livestock.image_url else [],
        "weight": livestock.weight,
        "age_months": livestock.age_months,
        "age": livestock.age_months // 12 if livestock.age_months else 0,
        "gender": getattr(livestock, "gender", None),
        "description": getattr(livestock, "description", None),
        "health_certified": getattr(livestock, "health_certified", False),
        "price_per_kg": getattr(livestock, "price_per_kg", None),
        "original_price": getattr(livestock, "original_price", None),
        "seller": {
            "id": livestock.farmer.id,
            "first_name": livestock.farmer.first_name,
            "last_name": livestock.farmer.last_name,
            "farm_name": getattr(livestock.farmer, "farm_name", None),
            "phone": getattr(livestock.farmer, "phone", None),
        }
        if livestock.farmer
        else None,
        "vaccinations": [v.to_dict() for v in livestock.vaccinations]
        if livestock.vaccinations
        else [],
    }), 200


@api_bp.route("/livestock", methods=["POST"])
@jwt_required()
def create_livestock():
    """
    Create a new livestock listing.
    Protected endpoint for farmers.
    """
    current_user_id = get_jwt_identity()

    data = request.get_json()

    # Required fields
    required_fields = ["animal_type", "weight", "price", "location", "image_url"]
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"{field} is required"}), 400

    try:
        # Create livestock
        livestock = Livestock(
            farmer_id=current_user_id,
            animal_type=data["animal_type"],
            breed=data.get("breed"),
            gender=data.get("gender"),
            weight=data["weight"],
            age_months=data.get("age_months"),
            price=data["price"],
            price_per_kg=data.get("price_per_kg"),
            original_price=data.get("original_price"),
            location=data["location"],
            image_url=data["image_url"],
            images=data.get("images", ""),
            description=data.get("description"),
            reason_for_sale=data.get("reason_for_sale"),
            health_certified=data.get("health_certified", False),
        )

        db.session.add(livestock)
        db.session.flush()  # Get the livestock ID

        # Create vaccinations if provided
        vaccinations = data.get("vaccinations", [])
        for vax_data in vaccinations:
            if vax_data.get("name") and vax_data.get("date_administered"):
                try:
                    date_administered = datetime.strptime(
                        vax_data["date_administered"], "%Y-%m-%d"
                    ).date()
                except (ValueError, TypeError):
                    date_administered = None

                try:
                    next_due_date = (
                        datetime.strptime(vax_data["next_due_date"], "%Y-%m-%d").date()
                        if vax_data.get("next_due_date")
                        else None
                    )
                except (ValueError, TypeError):
                    next_due_date = None

                vaccination = Vaccination(
                    livestock_id=livestock.id,
                    name=vax_data["name"],
                    date_administered=date_administered,
                    next_due_date=next_due_date,
                    certificate_url=vax_data.get("certificate_url"),
                )
                db.session.add(vaccination)

        db.session.commit()

        return jsonify({
            "message": "Livestock created successfully",
            "livestock": livestock.to_dict(),
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


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
