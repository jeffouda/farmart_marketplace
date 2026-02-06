"""
Public API Routes
Provides RESTful endpoints for livestock listings and orders with filtering
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
<<<<<<< HEAD
from datetime import datetime
import uuid
from app.models import Livestock, Order, User, UserAddress, OrderStatus
from app.utils.decorators import farmer_required
=======
from app.models import Livestock, Order, User, Vaccination
>>>>>>> origin/main
from app import db
from datetime import datetime

# Create a new blueprint with /api prefix
api_bp = Blueprint("api", __name__, url_prefix="/api")


# ==================== Livestock Routes ====================

@api_bp.route("/livestock", methods=["GET"])
def get_livestock():
    """
    Get all available livestock for sale with filtering.
    Public endpoint for the marketplace.
    
    Query Parameters:
        - type: Filter by animal type (e.g., Goat, Cow, Sheep)
        - breed: Filter by breed
        - min_price: Minimum price filter
        - max_price: Maximum price filter
        - location: Filter by location
        - sort_by: Sort option (newest, price-low, price-high)
        - page: Page number for pagination
        - per_page: Items per page
    """
    # Get query parameters for filtering
    animal_type = request.args.get("type") or request.args.get("species")
    breed = request.args.get("breed")
    min_price = request.args.get("min_price") or request.args.get("minPrice")
    max_price = request.args.get("max_price") or request.args.get("maxPrice")
    location = request.args.get("location")
    sort_by = request.args.get("sort_by") or request.args.get("sortBy", "newest")
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 50, type=int)

    # Build query - filter by is_available = True
    query = Livestock.query.filter_by(is_available=True)

    # Apply filters
    if animal_type:
        query = query.filter(Livestock.animal_type.ilike(f"%{animal_type}%"))
    if breed:
        query = query.filter(Livestock.breed.ilike(f"%{breed}%"))
    if min_price:
        try:
            query = query.filter(Livestock.price >= float(min_price))
        except ValueError:
            pass
    if max_price:
        try:
            query = query.filter(Livestock.price <= float(max_price))
        except ValueError:
            pass
    if location:
        query = query.filter(Livestock.location.ilike(f"%{location}%"))

    # Sort options
    if sort_by == "price-low":
        query = query.order_by(Livestock.price.asc())
    elif sort_by == "price-high":
        query = query.order_by(Livestock.price.desc())
    else:
        query = query.order_by(Livestock.created_at.desc())

    # Paginate results
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    livestock = pagination.items

<<<<<<< HEAD
    return jsonify({
        "livestock": [item.to_dict() for item in livestock],
        "total": pagination.total,
        "page": pagination.page,
        "per_page": pagination.per_page,
        "pages": pagination.pages,
    }), 200


@api_bp.route("/livestock/<int:livestock_id>", methods=["GET"])
def get_livestock_detail(livestock_id):
    """
    Get detailed livestock information by ID.
    Public endpoint - includes farmer info and health notes.
    """
    livestock = Livestock.query.get(livestock_id)

    if not livestock:
        return jsonify({"error": "Livestock not found"}), 404

    if not livestock.is_available:
        return jsonify({"error": "Livestock is no longer available"}), 404

    # Get farmer information
    farmer = User.query.get(livestock.farmer_id)
    farmer_info = None
    if farmer:
        farmer_info = {
            "id": farmer.id,
            "first_name": farmer.first_name,
            "last_name": farmer.last_name,
            "full_name": f"{farmer.first_name} {farmer.last_name}",
            "phone": farmer.phone_number,
            "location": farmer.profile.location if farmer.profile else None,
            "rating": farmer.profile.rating if farmer.profile else 0,
            "total_sales": farmer.profile.total_sales if farmer.profile else 0,
=======
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
>>>>>>> origin/main
        }

    response_data = livestock.to_dict()
    response_data["farmer"] = farmer_info
    
    return jsonify(response_data), 200


@api_bp.route("/livestock", methods=["POST"])
@farmer_required
def create_livestock():
    """
    Create a new livestock listing.
    Requires farmer authentication.
    """
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


@api_bp.route("/livestock/<int:livestock_id>", methods=["PUT"])
@farmer_required
def update_livestock(livestock_id):
    """
    Update a livestock listing.
    Only the owner farmer can update.
    """
    farmer_id = get_jwt_identity()
    livestock = Livestock.query.get(livestock_id)

    if not livestock:
        return jsonify({"error": "Livestock not found"}), 404

    if livestock.farmer_id != farmer_id:
        return jsonify({"error": "You can only update your own listings"}), 403

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


@api_bp.route("/livestock/<int:livestock_id>", methods=["DELETE"])
@farmer_required
def delete_livestock(livestock_id):
    """
    Delete a livestock listing.
    Only the owner farmer can delete.
    """
    farmer_id = get_jwt_identity()
    livestock = Livestock.query.get(livestock_id)

    if not livestock:
        return jsonify({"error": "Livestock not found"}), 404

    if livestock.farmer_id != farmer_id:
        return jsonify({"error": "You can only delete your own listings"}), 403

    try:
        db.session.delete(livestock)
        db.session.commit()
        return jsonify({"message": "Livestock deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# ==================== Order Routes ====================

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

    status = request.args.get("status")
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    query = Order.query.filter_by(buyer_id=current_user_id)

    if status:
        query = query.filter(Order.status == status)

    pagination = query.order_by(Order.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        "orders": [
            {
                "id": order.id,
                "order_number": order.order_number,
                "livestock": {
                    "id": order.livestock.id,
                    "name": order.livestock.animal_type,
                    "species": order.livestock.animal_type,
                    "breed": order.livestock.breed,
                    "price": float(order.livestock.price),
                }
                if order.livestock
                else None,
                "quantity": order.quantity,
                "total_amount": float(order.total_amount),
                "status": order.status,
                "created_at": order.created_at.isoformat() if order.created_at else None,
            }
            for order in pagination.items
        ],
        "total": pagination.total,
        "page": pagination.page,
        "per_page": pagination.per_page,
        "pages": pagination.pages,
    }), 200


@api_bp.route("/orders/<int:order_id>", methods=["GET"])
@jwt_required()
def get_order_detail(order_id):
    """
    Get order details by ID.
    """
    current_user_id = get_jwt_identity()
    order = Order.query.get(order_id)

    if not order:
        return jsonify({"error": "Order not found"}), 404

    # Check if user is the buyer or the farmer who owns the livestock
    if order.buyer_id != current_user_id:
        if not order.livestock or order.livestock.farmer_id != current_user_id:
            return jsonify({"error": "Access denied"}), 403

    return jsonify({
        "order": order.to_dict(),
        "buyer": {
            "id": order.buyer.id,
            "name": f"{order.buyer.first_name} {order.buyer.last_name}",
            "phone": order.buyer.phone_number,
        } if order.buyer else None,
        "payment": {
            "status": order.payment.status if order.payment else None,
            "amount": float(order.payment.amount) if order.payment else None,
        } if order.payment else None,
    }), 200


@api_bp.route("/orders", methods=["POST"])
@jwt_required()
def create_order():
    """
    Place a new order for livestock.
    """
    current_user_id = get_jwt_identity()
    data = request.get_json()

    # Validate required fields
    livestock_id = data.get("livestock_id")
    shipping_address = data.get("shipping_address")

    if not livestock_id:
        return jsonify({"error": "Livestock ID is required"}), 400
    if not shipping_address:
        return jsonify({"error": "Shipping address is required"}), 400

    # Get livestock
    livestock = Livestock.query.get(livestock_id)
    if not livestock:
        return jsonify({"error": "Livestock not found"}), 404

    if not livestock.is_available:
        return jsonify({"error": "Livestock is not available"}), 400

    # Prevent farmers from buying their own livestock
    if livestock.farmer_id == current_user_id:
        return jsonify({"error": "You cannot purchase your own livestock"}), 400

    # Calculate totals
    quantity = data.get("quantity", 1)
    subtotal = float(livestock.price) * quantity
    commission_rate = 0.02  # 2% commission
    commission_amount = subtotal * commission_rate
    total_amount = subtotal + commission_amount

    # Generate order number
    order_number = f"ORD-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{current_user_id}"

    try:
        order = Order(
            order_number=order_number,
            buyer_id=current_user_id,
            livestock_id=livestock.id,
            quantity=quantity,
            unit_price=livestock.price,
            subtotal=subtotal,
            commission_rate=commission_rate,
            commission_amount=commission_amount,
            total_amount=total_amount,
            shipping_address=shipping_address,
            buyer_notes=data.get("buyer_notes"),
            status=OrderStatus.PENDING,
        )

        # Mark livestock as reserved
        livestock.is_available = False

        db.session.add(order)
        db.session.commit()

        return jsonify({
            "message": "Order placed successfully",
            "order": order.to_dict(),
            "payment_required": float(order.total_amount),
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@api_bp.route("/orders/<int:order_id>/status", methods=["PUT"])
@jwt_required()
def update_order_status(order_id):
    """
    Update order status.
    Farmers can update to: confirmed, shipped
    Buyers can update to: cancelled (if pending), delivered (if shipped)
    """
    current_user_id = get_jwt_identity()
    order = Order.query.get(order_id)

    if not order:
        return jsonify({"error": "Order not found"}), 404

    data = request.get_json()
    new_status = data.get("status")

    if not new_status:
        return jsonify({"error": "Status is required"}), 400

    # Check permissions and valid transitions
    is_buyer = order.buyer_id == current_user_id
    is_farmer = order.livestock and order.livestock.farmer_id == current_user_id

    if not is_buyer and not is_farmer:
        return jsonify({"error": "Access denied"}), 403

    valid_transitions = {
        "pending": ["confirmed", "cancelled"],
        "confirmed": ["processing", "cancelled"],
        "processing": ["shipped", "cancelled"],
        "shipped": ["delivered"],
        "delivered": [],
        "cancelled": [],
    }

    if new_status not in valid_transitions.get(order.status, []):
        return jsonify({
            "error": f"Cannot change status from '{order.status}' to '{new_status}'"
        }), 400

    # Role-based permissions for certain transitions
    if new_status in ["confirmed", "processing", "shipped"] and not is_farmer:
        return jsonify({"error": "Only the farmer can update this status"}), 403

    if new_status == "delivered" and not is_buyer:
        return jsonify({"error": "Only the buyer can confirm delivery"}), 403

    try:
        order.status = new_status
        
        if new_status == "confirmed":
            order.confirmed_at = datetime.utcnow()
        elif new_status == "shipped":
            order.shipped_at = datetime.utcnow()
        elif new_status == "delivered":
            order.delivered_at = datetime.utcnow()
        elif new_status == "cancelled":
            order.cancelled_at = datetime.utcnow()
            order.cancellation_reason = data.get("reason", "Order cancelled")
            # Make livestock available again
            if order.livestock:
                order.livestock.is_available = True

        db.session.commit()

        return jsonify({
            "message": f"Order status updated to '{new_status}'",
            "order": order.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
