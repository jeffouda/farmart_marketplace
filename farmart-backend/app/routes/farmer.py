"""
Farmer Routes
Livestock CRUD, Bulk Upload, Analytics logic
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
from datetime import datetime, timedelta
from app.models import (
    User,
    Livestock,
    LivestockImage,
    HealthRecord,
    Order,
    Payment,
    UserRole,
    LivestockStatus,
    OrderStatus,
)
from app import db
from app.services.file_handler import FileHandler
from app.services.escrow_manager import EscrowManager
from app.utils.decorators import farmer_required

farmer_bp = Blueprint("farmer", __name__)


@farmer_bp.route("/livestock", methods=["POST"])
@jwt_required()
@farmer_required
def create_livestock():
    """Create a new livestock listing."""
    current_user_id = get_jwt_identity()
    data = request.get_json()

    required_fields = ["name", "species", "price"]
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"Missing required field: {field}"}), 400

    livestock = Livestock(
        farmer_id=current_user_id,
        name=data["name"],
        species=data["species"],
        breed=data.get("breed"),
        gender=data.get("gender"),
        age_years=data.get("age_years"),
        age_months=data.get("age_months"),
        weight_kg=data.get("weight_kg"),
        color=data.get("color"),
        description=data.get("description"),
        health_status=data.get("health_status"),
        price=data["price"],
        currency=data.get("currency", "KES"),
    )

    db.session.add(livestock)
    db.session.commit()

    images = data.get("images", [])
    for idx, image_url in enumerate(images):
        img = LivestockImage(
            livestock_id=livestock.id, image_url=image_url, is_primary=(idx == 0)
        )
        db.session.add(img)

    db.session.commit()

    return jsonify({
        "message": "Livestock listing created successfully",
        "livestock": livestock.to_dict(),
    }), 201


@farmer_bp.route("/livestock", methods=["GET"])
@jwt_required()
@farmer_required
def get_my_livestock():
    """Get all livestock listings for the current farmer."""
    current_user_id = get_jwt_identity()

    status = request.args.get("status")
    species = request.args.get("species")
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    query = Livestock.query.filter_by(farmer_id=current_user_id)

    if status:
        query = query.filter_by(status=status)
    if species:
        query = query.filter_by(species=species)

    pagination = query.order_by(Livestock.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        "livestock": [item.to_dict() for item in pagination.items],
        "total": pagination.total,
        "page": pagination.page,
        "per_page": pagination.per_page,
        "pages": pagination.pages,
    }), 200


@farmer_bp.route("/livestock/<int:livestock_id>", methods=["GET"])
@jwt_required()
@farmer_required
def get_livestock_detail(livestock_id):
    """Get details of a specific livestock listing."""
    current_user_id = get_jwt_identity()
    livestock = Livestock.query.filter_by(
        id=livestock_id, farmer_id=current_user_id
    ).first()

    if not livestock:
        return jsonify({"error": "Livestock not found"}), 404

    return jsonify({
        "livestock": livestock.to_dict(),
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


@farmer_bp.route("/livestock/<int:livestock_id>", methods=["PUT"])
@jwt_required()
@farmer_required
def update_livestock(livestock_id):
    """Update a livestock listing."""
    current_user_id = get_jwt_identity()
    livestock = Livestock.query.filter_by(
        id=livestock_id, farmer_id=current_user_id
    ).first()

    if not livestock:
        return jsonify({"error": "Livestock not found"}), 404

    data = request.get_json()

    updatable_fields = [
        "name",
        "species",
        "breed",
        "gender",
        "age_years",
        "age_months",
        "weight_kg",
        "color",
        "description",
        "health_status",
        "price",
        "status",
    ]

    for field in updatable_fields:
        if field in data:
            setattr(livestock, field, data[field])

    db.session.commit()

    return jsonify({
        "message": "Livestock updated successfully",
        "livestock": livestock.to_dict(),
    }), 200


@farmer_bp.route("/livestock/<int:livestock_id>", methods=["DELETE"])
@jwt_required()
@farmer_required
def delete_livestock(livestock_id):
    """Delete a livestock listing."""
    current_user_id = get_jwt_identity()
    livestock = Livestock.query.filter_by(
        id=livestock_id, farmer_id=current_user_id
    ).first()

    if not livestock:
        return jsonify({"error": "Livestock not found"}), 404

    if livestock.status == LivestockStatus.SOLD:
        return jsonify({"error": "Cannot delete sold livestock"}), 400

    db.session.delete(livestock)
    db.session.commit()

    return jsonify({"message": "Livestock deleted successfully"}), 200


@farmer_bp.route("/livestock/<int:livestock_id>/health-record", methods=["POST"])
@jwt_required()
@farmer_required
def add_health_record(livestock_id):
    """Add a health record to livestock."""
    current_user_id = get_jwt_identity()
    livestock = Livestock.query.filter_by(
        id=livestock_id, farmer_id=current_user_id
    ).first()

    if not livestock:
        return jsonify({"error": "Livestock not found"}), 404

    data = request.get_json()

    health_record = HealthRecord(
        livestock_id=livestock_id,
        record_type=data["record_type"],
        record_date=datetime.strptime(data["record_date"], "%Y-%m-%d").date(),
        description=data.get("description"),
        veterinarian_name=data.get("veterinarian_name"),
        document_url=data.get("document_url"),
        next_due_date=datetime.strptime(data["next_due_date"], "%Y-%m-%d").date()
        if data.get("next_due_date")
        else None,
    )

    db.session.add(health_record)
    db.session.commit()

    return jsonify({
        "message": "Health record added successfully",
        "health_record": {
            "id": health_record.id,
            "record_type": health_record.record_type,
            "record_date": health_record.record_date.isoformat(),
        },
    }), 201


@farmer_bp.route("/bulk-upload", methods=["POST"])
@jwt_required()
@farmer_required
def bulk_upload():
    """Bulk upload livestock from CSV/Excel file."""
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    try:
        result = FileHandler.parse_livestock_file(file)

        current_user_id = get_jwt_identity()
        created = 0
        errors = []

        for idx, row in enumerate(result["data"]):
            try:
                livestock = Livestock(
                    farmer_id=current_user_id,
                    name=row.get("name", f"Animal {idx + 1}"),
                    species=row["species"],
                    breed=row.get("breed"),
                    gender=row.get("gender"),
                    age_years=row.get("age_years"),
                    age_months=row.get("age_months"),
                    weight_kg=row.get("weight_kg"),
                    health_status=row.get("health_status", "healthy"),
                    price=row["price"],
                )
                db.session.add(livestock)
                created += 1
            except Exception as e:
                errors.append(f"Row {idx + 1}: {str(e)}")

        db.session.commit()

        return jsonify({
            "message": f"Bulk upload completed. Created {created} livestock entries.",
            "created": created,
            "errors": errors if errors else None,
            "summary": result.get("summary"),
        }), 201

    except Exception as e:
        return jsonify({"error": f"Failed to parse file: {str(e)}"}), 400


@farmer_bp.route("/analytics", methods=["GET"])
@jwt_required()
@farmer_required
def get_analytics():
    """Get farmer analytics dashboard."""
    current_user_id = get_jwt_identity()

    period = request.args.get("period", "month")
    today = datetime.utcnow().date()

    if period == "week":
        start_date = today - timedelta(days=7)
    elif period == "month":
        start_date = today - timedelta(days=30)
    else:
        start_date = today - timedelta(days=365)

    total_listings = Livestock.query.filter_by(farmer_id=current_user_id).count()

    active_listings = Livestock.query.filter_by(
        farmer_id=current_user_id, status=LivestockStatus.AVAILABLE
    ).count()

    orders_in_period = (
        Order.query
        .join(Livestock)
        .filter(
            Livestock.farmer_id == current_user_id,
            Order.status.in_([OrderStatus.DELIVERED, OrderStatus.CONFIRMED]),
            Order.placed_at >= start_date,
        )
        .count()
    )

    revenue_in_period = (
        db.session
        .query(func.sum(Order.total_amount))
        .join(Livestock)
        .filter(
            Livestock.farmer_id == current_user_id,
            Order.status.in_([OrderStatus.DELIVERED, OrderStatus.CONFIRMED]),
            Order.placed_at >= start_date,
        )
        .scalar()
        or 0
    )

    commission_earned = float(revenue_in_period) * 0.02

    recent_orders = (
        Order.query
        .join(Livestock)
        .filter(Livestock.farmer_id == current_user_id)
        .order_by(Order.placed_at.desc())
        .limit(10)
        .all()
    )

    return jsonify({
        "period": period,
        "start_date": start_date.isoformat(),
        "end_date": today.isoformat(),
        "listings": {"total": total_listings, "active": active_listings},
        "sales": {
            "revenue_in_period": float(revenue_in_period),
            "commission_earned": commission_earned,
            "orders_in_period": orders_in_period,
        },
        "recent_orders": [order.to_dict() for order in recent_orders],
    }), 200


@farmer_bp.route("/orders", methods=["GET"])
@jwt_required()
@farmer_required
def get_orders():
    """Get orders for farmer's livestock."""
    current_user_id = get_jwt_identity()

    status = request.args.get("status")
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    query = Order.query.join(Livestock).filter(Livestock.farmer_id == current_user_id)

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


@farmer_bp.route("/orders/<int:order_id>/confirm", methods=["POST"])
@jwt_required()
@farmer_required
def confirm_order(order_id):
    """Confirm an order (farmer accepts)."""
    current_user_id = get_jwt_identity()

    order = (
        Order.query
        .join(Livestock)
        .filter(Order.id == order_id, Livestock.farmer_id == current_user_id)
        .first()
    )

    if not order:
        return jsonify({"error": "Order not found"}), 404

    if order.status != OrderStatus.PENDING:
        return jsonify({"error": "Order cannot be confirmed"}), 400

    order.status = OrderStatus.CONFIRMED
    order.confirmed_at = datetime.utcnow()

    livestock = Livestock.query.get(order.livestock_id)
    if livestock:
        livestock.status = LivestockStatus.RESERVED

    db.session.commit()

    return jsonify({
        "message": "Order confirmed successfully",
        "order": order.to_dict(),
    }), 200


@farmer_bp.route("/orders/<int:order_id>/ship", methods=["POST"])
@jwt_required()
@farmer_required
def ship_order(order_id):
    """Mark order as shipped."""
    current_user_id = get_jwt_identity()

    order = (
        Order.query
        .join(Livestock)
        .filter(Order.id == order_id, Livestock.farmer_id == current_user_id)
        .first()
    )

    if not order:
        return jsonify({"error": "Order not found"}), 404

    if order.status != OrderStatus.CONFIRMED:
        return jsonify({"error": "Order cannot be shipped"}), 400

    order.status = OrderStatus.SHIPPED
    order.shipped_at = datetime.utcnow()

    db.session.commit()

    return jsonify({
        "message": "Order shipped successfully",
        "order": order.to_dict(),
    }), 200


@farmer_bp.route("/payouts", methods=["GET"])
@jwt_required()
@farmer_required
def get_payouts():
    """Get farmer payout history."""
    current_user_id = get_jwt_identity()

    payouts = (
        db.session
        .query(Order, Payment)
        .join(Livestock, Order.livestock_id == Livestock.id)
        .join(Payment, Order.id == Payment.order_id)
        .filter(
            Livestock.farmer_id == current_user_id,
            Order.status == OrderStatus.DELIVERED,
            Payment.status == "completed",
        )
        .all()
    )

    return jsonify({
        "payouts": [
            {
                "order_id": order.id,
                "order_number": order.order_number,
                "amount": float(order.total_amount),
                "commission": float(order.commission_amount),
                "payout_amount": float(order.total_amount)
                - float(order.commission_amount),
                "payment_date": payment.payment_date.isoformat()
                if payment.payment_date
                else None,
            }
            for order, payment in payouts
        ]
    }), 200
