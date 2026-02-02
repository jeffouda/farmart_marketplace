"""
Buyer Routes
Search/Filter, Cart, Order placement
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func, or_
from datetime import datetime
from app.models import (
    User,
    Livestock,
    UserAddress,
    Order,
    Payment,
    LivestockStatus,
    OrderStatus,
)
from app import db
from app.services.escrow_manager import EscrowManager

buyer_bp = Blueprint("buyer", __name__)


@buyer_bp.route("/search", methods=["GET"])
def search_livestock():
    """Search and filter livestock listings."""
    q = request.args.get("q", "")
    species = request.args.get("species")
    breed = request.args.get("breed")
    gender = request.args.get("gender")
    min_price = request.args.get("min_price", type=float)
    max_price = request.args.get("max_price", type=float)
    min_weight = request.args.get("min_weight", type=float)
    max_weight = request.args.get("max_weight", type=float)
    health_status = request.args.get("health_status")
    sort = request.args.get("sort", "created_at")
    order_dir = request.args.get("order", "desc")
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 12, type=int)

    query = Livestock.query.filter_by(status=LivestockStatus.AVAILABLE)

    if q:
        search_term = f"%{q}%"
        query = query.filter(
            or_(
                Livestock.name.ilike(search_term),
                Livestock.species.ilike(search_term),
                Livestock.breed.ilike(search_term),
                Livestock.description.ilike(search_term),
            )
        )

    if species:
        query = query.filter(Livestock.species == species)
    if breed:
        query = query.filter(Livestock.breed.ilike(f"%{breed}%"))
    if gender:
        query = query.filter(Livestock.gender == gender)
    if min_price:
        query = query.filter(Livestock.price >= min_price)
    if max_price:
        query = query.filter(Livestock.price <= max_price)
    if min_weight:
        query = query.filter(Livestock.weight_kg >= min_weight)
    if max_weight:
        query = query.filter(Livestock.weight_kg <= max_weight)
    if health_status:
        query = query.filter(Livestock.health_status == health_status)

    sort_column = getattr(Livestock, sort, Livestock.created_at)
    if order_dir == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "livestock": [item.to_dict() for item in pagination.items],
        "total": pagination.total,
        "page": pagination.page,
        "per_page": pagination.per_page,
        "pages": pagination.pages,
    }), 200


@buyer_bp.route("/livestock/<int:livestock_id>", methods=["GET"])
def get_livestock_detail(livestock_id):
    """Get detailed livestock information."""
    livestock = Livestock.query.filter_by(
        id=livestock_id, status=LivestockStatus.AVAILABLE
    ).first()

    if not livestock:
        return jsonify({"error": "Livestock not found or not available"}), 404

    livestock.view_count += 1
    db.session.commit()

    farmer = User.query.get(livestock.farmer_id)

    return jsonify({
        "livestock": livestock.to_dict(),
        "farmer": {
            "id": farmer.id,
            "first_name": farmer.first_name,
            "last_name": farmer.last_name,
            "location": farmer.profile.location if farmer.profile else None,
            "rating": farmer.profile.rating if farmer.profile else None,
            "total_sales": farmer.profile.total_sales if farmer.profile else 0,
        },
        "health_records": [
            {
                "id": hr.id,
                "record_type": hr.record_type,
                "record_date": hr.record_date.isoformat() if hr.record_date else None,
                "description": hr.description,
                "veterinarian_name": hr.veterinarian_name,
            }
            for hr in livestock.health_records
        ],
    }), 200


@buyer_bp.route("/species", methods=["GET"])
def get_species():
    """Get all available species and their counts."""
    species_counts = (
        db.session
        .query(Livestock.species, func.count(Livestock.id))
        .filter_by(status=LivestockStatus.AVAILABLE)
        .group_by(Livestock.species)
        .all()
    )

    return jsonify({
        "species": [
            {"name": species, "count": count} for species, count in species_counts
        ]
    }), 200


# In-memory cart for demo (use Redis/database in production)
cart = {}


@buyer_bp.route("/cart", methods=["GET"])
@jwt_required()
def get_cart():
    """Get current user's cart."""
    current_user_id = get_jwt_identity()
    user_cart = cart.get(current_user_id, [])

    cart_items = []
    total = 0

    for item in user_cart:
        livestock = Livestock.query.get(item["livestock_id"])
        if livestock:
            item_total = float(livestock.price) * item["quantity"]
            total += item_total
            cart_items.append({
                "livestock_id": livestock.id,
                "name": livestock.name,
                "species": livestock.species,
                "price": float(livestock.price),
                "quantity": item["quantity"],
                "total": item_total,
                "image": livestock.images[0].image_url if livestock.images else None,
            })

    return jsonify({
        "items": cart_items,
        "total": total,
        "item_count": len(cart_items),
    }), 200


@buyer_bp.route("/cart/add", methods=["POST"])
@jwt_required()
def add_to_cart():
    """Add item to cart."""
    current_user_id = get_jwt_identity()
    data = request.get_json()

    livestock_id = data.get("livestock_id")
    quantity = data.get("quantity", 1)

    if not livestock_id:
        return jsonify({"error": "Livestock ID is required"}), 400

    livestock = Livestock.query.get(livestock_id)
    if not livestock:
        return jsonify({"error": "Livestock not found"}), 404

    if livestock.status != LivestockStatus.AVAILABLE:
        return jsonify({"error": "Livestock is not available"}), 400

    if current_user_id not in cart:
        cart[current_user_id] = []

    for item in cart[current_user_id]:
        if item["livestock_id"] == livestock_id:
            item["quantity"] += quantity
            break
    else:
        cart[current_user_id].append({
            "livestock_id": livestock_id,
            "quantity": quantity,
        })

    return jsonify({
        "message": "Added to cart",
        "cart_count": len(cart[current_user_id]),
    }), 200


@buyer_bp.route("/cart/remove", methods=["POST"])
@jwt_required()
def remove_from_cart():
    """Remove item from cart."""
    current_user_id = get_jwt_identity()
    data = request.get_json()

    livestock_id = data.get("livestock_id")

    if not livestock_id:
        return jsonify({"error": "Livestock ID is required"}), 400

    if current_user_id in cart:
        cart[current_user_id] = [
            item
            for item in cart[current_user_id]
            if item["livestock_id"] != livestock_id
        ]

    return jsonify({
        "message": "Removed from cart",
        "cart_count": len(cart.get(current_user_id, [])),
    }), 200


@buyer_bp.route("/cart/clear", methods=["POST"])
@jwt_required()
def clear_cart():
    """Clear user's cart."""
    current_user_id = get_jwt_identity()
    cart[current_user_id] = []

    return jsonify({"message": "Cart cleared"}), 200


@buyer_bp.route("/addresses", methods=["GET"])
@jwt_required()
def get_addresses():
    """Get user's saved addresses."""
    current_user_id = get_jwt_identity()
    addresses = (
        UserAddress.query
        .filter_by(user_id=current_user_id)
        .order_by(UserAddress.is_default.desc())
        .all()
    )

    return jsonify({
        "addresses": [
            {
                "id": addr.id,
                "label": addr.label,
                "recipient_name": addr.recipient_name,
                "recipient_phone": addr.recipient_phone,
                "street_address": addr.street_address,
                "city": addr.city,
                "county": addr.county,
                "is_default": addr.is_default,
            }
            for addr in addresses
        ]
    }), 200


@buyer_bp.route("/addresses", methods=["POST"])
@jwt_required()
def add_address():
    """Add a new address."""
    current_user_id = get_jwt_identity()
    data = request.get_json()

    address = UserAddress(
        user_id=current_user_id,
        label=data.get("label", "Default"),
        recipient_name=data["recipient_name"],
        recipient_phone=data["recipient_phone"],
        street_address=data["street_address"],
        city=data["city"],
        county=data.get("county"),
        postal_code=data.get("postal_code"),
        is_default=data.get("is_default", False),
    )

    if address.is_default:
        UserAddress.query.filter_by(user_id=current_user_id, is_default=True).update({
            "is_default": False
        })

    db.session.add(address)
    db.session.commit()

    return jsonify({
        "message": "Address added successfully",
        "address_id": address.id,
    }), 201


@buyer_bp.route("/addresses/<int:address_id>", methods=["DELETE"])
@jwt_required()
def delete_address(address_id):
    """Delete an address."""
    current_user_id = get_jwt_identity()
    address = UserAddress.query.filter_by(
        id=address_id, user_id=current_user_id
    ).first()

    if not address:
        return jsonify({"error": "Address not found"}), 404

    db.session.delete(address)
    db.session.commit()

    return jsonify({"message": "Address deleted successfully"}), 200


@buyer_bp.route("/orders", methods=["POST"])
@jwt_required()
def place_order():
    """Place a new order."""
    current_user_id = get_jwt_identity()
    data = request.get_json()

    required_fields = ["livestock_id", "address_id"]
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"Missing required field: {field}"}), 400

    livestock = Livestock.query.get(data["livestock_id"])
    if not livestock:
        return jsonify({"error": "Livestock not found"}), 404

    if livestock.status != LivestockStatus.AVAILABLE:
        return jsonify({"error": "Livestock is not available"}), 400

    address = UserAddress.query.filter_by(
        id=data["address_id"], user_id=current_user_id
    ).first()

    if not address:
        return jsonify({"error": "Address not found"}), 404

    quantity = data.get("quantity", 1)
    subtotal = float(livestock.price) * quantity
    commission_rate = 0.02
    commission_amount = subtotal * commission_rate

    order_number = f"ORD-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{current_user_id}"

    order = Order(
        order_number=order_number,
        buyer_id=current_user_id,
        livestock_id=livestock.id,
        quantity=quantity,
        unit_price=livestock.price,
        subtotal=subtotal,
        commission_rate=commission_rate,
        commission_amount=commission_amount,
        total_amount=subtotal,
        shipping_address=f"{address.recipient_name}, {address.street_address}, {address.city}, {address.county}",
        buyer_notes=data.get("buyer_notes"),
    )

    livestock.status = LivestockStatus.RESERVED

    db.session.add(order)
    db.session.commit()

    return jsonify({
        "message": "Order placed successfully",
        "order": order.to_dict(),
        "payment_required": float(order.total_amount),
    }), 201


@buyer_bp.route("/orders", methods=["GET"])
@jwt_required()
def get_my_orders():
    """Get current user's orders."""
    current_user_id = get_jwt_identity()

    status = request.args.get("status")
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    query = Order.query.filter_by(buyer_id=current_user_id)

    if status:
        query = query.filter(Order.status == status)

    pagination = query.order_by(Order.placed_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        "orders": [order.to_dict() for order in pagination.items],
        "total": pagination.total,
        "page": pagination.page,
        "per_page": pagination.per_page,
        "pages": pagination.pages,
    }), 200


@buyer_bp.route("/orders/<int:order_id>", methods=["GET"])
@jwt_required()
def get_order_detail(order_id):
    """Get order details."""
    current_user_id = get_jwt_identity()
    order = Order.query.filter_by(id=order_id, buyer_id=current_user_id).first()

    if not order:
        return jsonify({"error": "Order not found"}), 404

    return jsonify({
        "order": order.to_dict(),
        "payment": {
            "status": order.payment.status if order.payment else None,
            "amount": float(order.payment.amount) if order.payment else None,
        }
        if order.payment
        else None,
    }), 200


@buyer_bp.route("/orders/<int:order_id>/cancel", methods=["POST"])
@jwt_required()
def cancel_order(order_id):
    """Cancel an order (only pending orders)."""
    current_user_id = get_jwt_identity()
    order = Order.query.filter_by(id=order_id, buyer_id=current_user_id).first()

    if not order:
        return jsonify({"error": "Order not found"}), 404

    if order.status != OrderStatus.PENDING:
        return jsonify({"error": "Order cannot be cancelled"}), 400

    order.status = OrderStatus.CANCELLED
    order.cancelled_at = datetime.utcnow()
    order.cancellation_reason = request.get_json().get("reason", "Buyer cancelled")

    livestock = Livestock.query.get(order.livestock_id)
    if livestock:
        livestock.status = LivestockStatus.AVAILABLE

    db.session.commit()

    return jsonify({
        "message": "Order cancelled successfully",
        "order": order.to_dict(),
    }), 200


@buyer_bp.route("/orders/<int:order_id>/deliver", methods=["POST"])
@jwt_required()
def confirm_delivery(order_id):
    """Confirm order delivery (releases escrow to farmer)."""
    current_user_id = get_jwt_identity()
    order = Order.query.filter_by(id=order_id, buyer_id=current_user_id).first()

    if not order:
        return jsonify({"error": "Order not found"}), 404

    if order.status != OrderStatus.SHIPPED:
        return jsonify({"error": "Order is not shipped yet"}), 400

    order.status = OrderStatus.DELIVERED
    order.delivered_at = datetime.utcnow()

    EscrowManager.release_escrow(order.id)

    farmer = User.query.get(order.livestock.farmer_id)
    if farmer and farmer.profile:
        farmer.profile.total_sales += 1
        farmer.profile.rating = (
            farmer.profile.rating * (farmer.profile.total_sales - 1) + 5
        ) / farmer.profile.total_sales

    db.session.commit()

    return jsonify({
        "message": "Delivery confirmed. Funds released to farmer.",
        "order": order.to_dict(),
    }), 200


@buyer_bp.route("/disputes", methods=["POST"])
@jwt_required()
def create_dispute():
    """Create a dispute for an order."""
    from app.models import Dispute, DisputeStatus

    current_user_id = get_jwt_identity()
    data = request.get_json()

    order_id = data.get("order_id")
    if not order_id:
        return jsonify({"error": "Order ID is required"}), 400

    order = Order.query.filter_by(id=order_id, buyer_id=current_user_id).first()

    if not order:
        return jsonify({"error": "Order not found"}), 404

    existing_dispute = Dispute.query.filter_by(order_id=order_id).first()
    if existing_dispute:
        return jsonify({"error": "Dispute already exists for this order"}), 409

    dispute = Dispute(
        order_id=order_id,
        user_id=current_user_id,
        dispute_type=data["dispute_type"],
        description=data["description"],
        evidence_urls=str(data.get("evidence_urls", [])),
        status=DisputeStatus.OPEN,
    )

    order.status = OrderStatus.DISPUTE

    db.session.add(dispute)
    db.session.commit()

    return jsonify({
        "message": "Dispute created successfully",
        "dispute": {
            "id": dispute.id,
            "order_id": dispute.order_id,
            "status": dispute.status,
            "created_at": dispute.created_at.isoformat(),
        },
    }), 201
