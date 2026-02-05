"""
Farmer Routes
Livestock management for farmers: CRUD operations and analytics
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from app import db
from app.models import Livestock, Order
from app.utils.decorators import farmer_required

farmer_bp = Blueprint("farmer", __name__, url_prefix="/api/v1/farmer")


@farmer_bp.route("/livestock", methods=["POST"])
@farmer_required
def add_livestock():
    """Create a new livestock listing."""
    farmer_id = get_jwt_identity()
    data = request.get_json()

    # Validate required fields
    required_fields = ["animal_type", "weight", "price", "location"]
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"Missing required field: {field}"}), 400

    try:
        animal = Livestock(
            farmer_id=farmer_id,
            animal_type=data["animal_type"],
            breed=data.get("breed"),
            weight=float(data["weight"]),
            age_months=data.get("age_months"),
            price=float(data["price"]),
            location=data["location"],
            description=data.get("description"),
            images=data.get("images", []),
            health_notes=data.get("health_notes"),
            is_available=True
        )

        db.session.add(animal)
        db.session.commit()

        return jsonify({
            "message": "Livestock created successfully",
            "livestock": animal.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@farmer_bp.route("/livestock", methods=["GET"])
@farmer_required
def my_livestock():
    """Get all livestock for the current farmer."""
    farmer_id = get_jwt_identity()
    
    # Optional filters
    status = request.args.get("status")  # available, sold
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    query = Livestock.query.filter_by(farmer_id=farmer_id)

    if status == "available":
        query = query.filter_by(is_available=True)
    elif status == "sold":
        query = query.filter_by(is_available=False)

    pagination = query.order_by(Livestock.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        "livestock": [a.to_dict() for a in pagination.items],
        "total": pagination.total,
        "page": pagination.page,
        "per_page": pagination.per_page,
        "pages": pagination.pages,
    }), 200


@farmer_bp.route("/livestock/<int:livestock_id>", methods=["GET"])
@farmer_required
def get_livestock(livestock_id):
    """Get single livestock details."""
    farmer_id = get_jwt_identity()
    livestock = Livestock.query.filter_by(id=livestock_id, farmer_id=farmer_id).first()

    if not livestock:
        return jsonify({"error": "Livestock not found"}), 404

    return jsonify({"livestock": livestock.to_dict()}), 200


@farmer_bp.route("/livestock/<int:livestock_id>", methods=["PUT"])
@farmer_required
def update_livestock(livestock_id):
    """Update a livestock listing."""
    farmer_id = get_jwt_identity()
    livestock = Livestock.query.filter_by(id=livestock_id, farmer_id=farmer_id).first()

    if not livestock:
        return jsonify({"error": "Livestock not found or access denied"}), 404

    data = request.get_json()

    # Update fields if provided
    if "animal_type" in data:
        livestock.animal_type = data["animal_type"]
    if "breed" in data:
        livestock.breed = data["breed"]
    if "weight" in data:
        livestock.weight = float(data["weight"])
    if "age_months" in data:
        livestock.age_months = data["age_months"]
    if "price" in data:
        livestock.price = float(data["price"])
    if "location" in data:
        livestock.location = data["location"]
    if "is_available" in data:
        livestock.is_available = data["is_available"]
    if "description" in data:
        livestock.description = data["description"]
    if "images" in data:
        livestock.images = data["images"]
    if "health_notes" in data:
        livestock.health_notes = data["health_notes"]

    try:
        db.session.commit()
        return jsonify({
            "message": "Livestock updated successfully",
            "livestock": livestock.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@farmer_bp.route("/livestock/<int:livestock_id>", methods=["DELETE"])
@farmer_required
def delete_livestock(livestock_id):
    """Delete a livestock listing."""
    farmer_id = get_jwt_identity()
    livestock = Livestock.query.filter_by(id=livestock_id, farmer_id=farmer_id).first()

    if not livestock:
        return jsonify({"error": "Livestock not found or access denied"}), 404

    # Check if there are pending orders for this livestock
    pending_orders = Order.query.filter_by(
        livestock_id=livestock_id
    ).filter(Order.status.in_(["pending", "confirmed", "processing"])).count()

    if pending_orders > 0:
        return jsonify({
            "error": "Cannot delete livestock with pending orders"
        }), 400

    try:
        db.session.delete(livestock)
        db.session.commit()
        return jsonify({"message": "Livestock deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@farmer_bp.route("/orders", methods=["GET"])
@farmer_required
def get_farmer_orders():
    """Get all orders for the farmer's livestock."""
    farmer_id = get_jwt_identity()
    
    status = request.args.get("status")
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    # Get orders for livestock owned by this farmer
    query = Order.query.join(Livestock).filter(Livestock.farmer_id == farmer_id)

    if status:
        query = query.filter(Order.status == status)

    pagination = query.order_by(Order.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        "orders": [order.to_dict() for order in pagination.items],
        "total": pagination.total,
        "page": pagination.page,
        "per_page": pagination.per_page,
        "pages": pagination.pages,
    }), 200


@farmer_bp.route("/analytics", methods=["GET"])
@farmer_required
def farmer_analytics():
    """Get farmer dashboard analytics."""
    farmer_id = get_jwt_identity()

    # Livestock stats
    total_animals = Livestock.query.filter_by(farmer_id=farmer_id).count()
    available_animals = Livestock.query.filter_by(
        farmer_id=farmer_id, is_available=True
    ).count()
    sold_animals = Livestock.query.filter_by(
        farmer_id=farmer_id, is_available=False
    ).count()

    total_value = db.session.query(
        db.func.sum(Livestock.price)
    ).filter_by(farmer_id=farmer_id, is_available=True).scalar() or 0

    # Order stats
    farmer_orders = Order.query.join(Livestock).filter(
        Livestock.farmer_id == farmer_id
    )
    
    total_orders = farmer_orders.count()
    pending_orders = farmer_orders.filter(Order.status == "pending").count()
    completed_orders = farmer_orders.filter(Order.status == "delivered").count()

    total_revenue = db.session.query(
        db.func.sum(Order.total_amount)
    ).join(Livestock).filter(
        Livestock.farmer_id == farmer_id,
        Order.status == "delivered"
    ).scalar() or 0

    return jsonify({
        "livestock": {
            "total": total_animals,
            "available": available_animals,
            "sold": sold_animals,
            "total_value": float(total_value),
        },
        "orders": {
            "total": total_orders,
            "pending": pending_orders,
            "completed": completed_orders,
            "total_revenue": float(total_revenue),
        }
    }), 200
