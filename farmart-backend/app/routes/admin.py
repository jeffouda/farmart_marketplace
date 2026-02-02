"""
Admin Routes
User moderation, Commission rules, Disputes
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from sqlalchemy import func
from app.models import (
    User,
    Livestock,
    Order,
    Dispute,
    CommissionRule,
    AuditLog,
    SystemSettings,
    UserRole,
    LivestockStatus,
    OrderStatus,
    DisputeStatus,
)
from app import db
from app.utils.decorators import admin_required

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/users", methods=["GET"])
@jwt_required()
@admin_required
def get_users():
    """Get all users with pagination and filtering."""
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    role = request.args.get("role")
    is_active = request.args.get("is_active")
    search = request.args.get("search")

    query = User.query

    if role:
        query = query.filter_by(role=role)
    if is_active is not None:
        query = query.filter_by(is_active=is_active.lower() == "true")
    if search:
        query = query.filter(
            (User.email.ilike(f"%{search}%"))
            | (User.first_name.ilike(f"%{search}%"))
            | (User.last_name.ilike(f"%{search}%"))
            | (User.phone_number.ilike(f"%{search}%"))
        )

    pagination = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        "users": [user.to_dict() for user in pagination.items],
        "total": pagination.total,
        "page": pagination.page,
        "per_page": pagination.per_page,
        "pages": pagination.pages,
    }), 200


@admin_bp.route("/users/<int:user_id>", methods=["GET"])
@jwt_required()
@admin_required
def get_user_detail(user_id):
    """Get user details including profile and stats."""
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    if user.role == UserRole.FARMER:
        total_listings = Livestock.query.filter_by(farmer_id=user_id).count()
        total_sales = (
            Order.query
            .join(Livestock)
            .filter(
                Livestock.farmer_id == user_id, Order.status == OrderStatus.DELIVERED
            )
            .count()
        )
        revenue = (
            db.session
            .query(func.sum(Order.total_amount))
            .join(Livestock)
            .filter(
                Livestock.farmer_id == user_id, Order.status == OrderStatus.DELIVERED
            )
            .scalar()
            or 0
        )
        stats = {
            "total_listings": total_listings,
            "total_sales": total_sales,
            "total_revenue": float(revenue),
        }
    else:
        total_orders = Order.query.filter_by(buyer_id=user_id).count()
        total_spent = (
            db.session
            .query(func.sum(Order.total_amount))
            .filter(Order.buyer_id == user_id, Order.status == OrderStatus.DELIVERED)
            .scalar()
            or 0
        )
        stats = {"total_orders": total_orders, "total_spent": float(total_spent)}

    return jsonify({
        "user": user.to_dict(),
        "profile": {
            "bio": user.profile.bio if user.profile else None,
            "location": user.profile.location if user.profile else None,
            "rating": user.profile.rating if user.profile else None,
            "id_number": user.profile.id_number if user.profile else None,
            "is_verified": user.profile.is_verified if user.profile else False,
        }
        if user.profile
        else None,
        "stats": stats,
    }), 200


@admin_bp.route("/users/<int:user_id>/activate", methods=["POST"])
@jwt_required()
@admin_required
def activate_user(user_id):
    """Activate a user account."""
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    user.is_active = True

    admin_id = get_jwt_identity()
    audit = AuditLog(
        admin_id=admin_id,
        action="user_activated",
        entity_type="user",
        entity_id=user_id,
        new_values={"is_active": True},
    )
    db.session.add(audit)
    db.session.commit()

    return jsonify({"message": "User activated successfully"}), 200


@admin_bp.route("/users/<int:user_id>/deactivate", methods=["POST"])
@jwt_required()
@admin_required
def deactivate_user(user_id):
    """Deactivate a user account."""
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    user.is_active = False

    admin_id = get_jwt_identity()
    audit = AuditLog(
        admin_id=admin_id,
        action="user_deactivated",
        entity_type="user",
        entity_id=user_id,
        old_values={"is_active": True},
        new_values={"is_active": False},
    )
    db.session.add(audit)
    db.session.commit()

    return jsonify({"message": "User deactivated successfully"}), 200


@admin_bp.route("/users/<int:user_id>/verify", methods=["POST"])
@jwt_required()
@admin_required
def verify_user(user_id):
    """Verify a user's identity."""
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    if user.profile:
        user.profile.id_number = request.get_json().get(
            "id_number", user.profile.id_number
        )
        user.profile.is_verified = True
    else:
        return jsonify({"error": "User profile not found"}), 404

    admin_id = get_jwt_identity()
    audit = AuditLog(
        admin_id=admin_id, action="user_verified", entity_type="user", entity_id=user_id
    )
    db.session.add(audit)
    db.session.commit()

    return jsonify({"message": "User verified successfully"}), 200


@admin_bp.route("/listings", methods=["GET"])
@jwt_required()
@admin_required
def get_all_listings():
    """Get all livestock listings across platform."""
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    status = request.args.get("status")
    species = request.args.get("species")

    query = Livestock.query

    if status:
        query = query.filter_by(status=status)
    if species:
        query = query.filter_by(species=species)

    pagination = query.order_by(Livestock.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        "listings": [item.to_dict() for item in pagination.items],
        "total": pagination.total,
        "page": pagination.page,
        "per_page": pagination.per_page,
        "pages": pagination.pages,
    }), 200


@admin_bp.route("/listings/<int:listing_id>/approve", methods=["POST"])
@jwt_required()
@admin_required
def approve_listing(listing_id):
    """Approve a livestock listing."""
    livestock = Livestock.query.get(listing_id)

    if not livestock:
        return jsonify({"error": "Listing not found"}), 404

    if livestock.status != LivestockStatus.PENDING_APPROVAL:
        return jsonify({"error": "Listing is not pending approval"}), 400

    livestock.status = LivestockStatus.AVAILABLE

    admin_id = get_jwt_identity()
    audit = AuditLog(
        admin_id=admin_id,
        action="listing_approved",
        entity_type="livestock",
        entity_id=listing_id,
    )
    db.session.add(audit)
    db.session.commit()

    return jsonify({"message": "Listing approved successfully"}), 200


@admin_bp.route("/listings/<int:listing_id>/reject", methods=["POST"])
@jwt_required()
@admin_required
def reject_listing(listing_id):
    """Reject a livestock listing."""
    livestock = Livestock.query.get(listing_id)

    if not livestock:
        return jsonify({"error": "Listing not found"}), 404

    reason = request.get_json().get("reason", "Does not meet platform standards")
    livestock.status = LivestockStatus.RESERVED

    admin_id = get_jwt_identity()
    audit = AuditLog(
        admin_id=admin_id,
        action="listing_rejected",
        entity_type="livestock",
        entity_id=listing_id,
        new_values={"reason": reason},
    )
    db.session.add(audit)
    db.session.commit()

    return jsonify({"message": "Listing rejected", "reason": reason}), 200


@admin_bp.route("/commission-rules", methods=["GET"])
@jwt_required()
@admin_required
def get_commission_rules():
    """Get all commission rules."""
    rules = CommissionRule.query.order_by(CommissionRule.created_at.desc()).all()

    return jsonify({
        "rules": [
            {
                "id": rule.id,
                "name": rule.name,
                "description": rule.description,
                "category": rule.category,
                "min_order_value": float(rule.min_order_value)
                if rule.min_order_value
                else None,
                "max_order_value": float(rule.max_order_value)
                if rule.max_order_value
                else None,
                "commission_rate": rule.commission_rate,
                "is_active": rule.is_active,
                "effective_from": rule.effective_from.isoformat()
                if rule.effective_from
                else None,
                "effective_to": rule.effective_to.isoformat()
                if rule.effective_to
                else None,
            }
            for rule in rules
        ]
    }), 200


@admin_bp.route("/commission-rules", methods=["POST"])
@jwt_required()
@admin_required
def create_commission_rule():
    """Create a new commission rule."""
    data = request.get_json()

    rule = CommissionRule(
        name=data["name"],
        description=data.get("description"),
        category=data.get("category"),
        min_order_value=data.get("min_order_value"),
        max_order_value=data.get("max_order_value"),
        commission_rate=data["commission_rate"],
        is_active=data.get("is_active", True),
        effective_from=datetime.strptime(data["effective_from"], "%Y-%m-%d").date()
        if data.get("effective_from")
        else None,
        effective_to=datetime.strptime(data["effective_to"], "%Y-%m-%d").date()
        if data.get("effective_to")
        else None,
    )

    db.session.add(rule)
    db.session.commit()

    return jsonify({
        "message": "Commission rule created successfully",
        "rule_id": rule.id,
    }), 201


@admin_bp.route("/commission-rules/<int:rule_id>", methods=["PUT"])
@jwt_required()
@admin_required
def update_commission_rule(rule_id):
    """Update a commission rule."""
    rule = CommissionRule.query.get(rule_id)

    if not rule:
        return jsonify({"error": "Commission rule not found"}), 404

    data = request.get_json()

    updatable_fields = [
        "name",
        "description",
        "category",
        "min_order_value",
        "max_order_value",
        "commission_rate",
        "is_active",
    ]

    for field in updatable_fields:
        if field in data:
            setattr(rule, field, data[field])

    db.session.commit()

    return jsonify({"message": "Commission rule updated successfully"}), 200


@admin_bp.route("/disputes", methods=["GET"])
@jwt_required()
@admin_required
def get_disputes():
    """Get all disputes."""
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    status = request.args.get("status")

    query = Dispute.query

    if status:
        query = query.filter_by(status=status)

    pagination = query.order_by(Dispute.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        "disputes": [
            {
                "id": d.id,
                "order_id": d.order_id,
                "user_id": d.user_id,
                "dispute_type": d.dispute_type,
                "description": d.description,
                "status": d.status,
                "created_at": d.created_at.isoformat(),
            }
            for d in pagination.items
        ],
        "total": pagination.total,
        "page": pagination.page,
        "per_page": pagination.per_page,
        "pages": pagination.pages,
    }), 200


@admin_bp.route("/disputes/<int:dispute_id>", methods=["GET"])
@jwt_required()
@admin_required
def get_dispute_detail(dispute_id):
    """Get dispute details with order info."""
    dispute = Dispute.query.get(dispute_id)

    if not dispute:
        return jsonify({"error": "Dispute not found"}), 404

    order = Order.query.get(dispute.order_id)

    return jsonify({
        "dispute": {
            "id": dispute.id,
            "order_id": dispute.order_id,
            "user_id": dispute.user_id,
            "dispute_type": dispute.dispute_type,
            "description": dispute.description,
            "evidence_urls": dispute.evidence_urls,
            "status": dispute.status,
            "admin_notes": dispute.admin_notes,
            "resolution": dispute.resolution,
            "amount_refunded": float(dispute.amount_refunded)
            if dispute.amount_refunded
            else None,
            "opened_at": dispute.opened_at.isoformat(),
            "resolved_at": dispute.resolved_at.isoformat()
            if dispute.resolved_at
            else None,
        },
        "order": order.to_dict() if order else None,
    }), 200


@admin_bp.route("/disputes/<int:dispute_id>/resolve", methods=["POST"])
@jwt_required()
@admin_required
def resolve_dispute(dispute_id):
    """Resolve a dispute."""
    dispute = Dispute.query.get(dispute_id)

    if not dispute:
        return jsonify({"error": "Dispute not found"}), 404

    data = request.get_json()

    resolution = data.get("resolution")
    refund_amount = data.get("amount_refunded")
    action = data.get("action")  # 'refund', 'release_escrow', 'partial'

    dispute.status = DisputeStatus.RESOLVED
    dispute.resolution = resolution
    dispute.admin_notes = data.get("admin_notes")
    dispute.resolved_at = datetime.utcnow()

    if refund_amount:
        dispute.amount_refunded = refund_amount

    order = Order.query.get(dispute.order_id)
    if order:
        if action == "refund":
            order.status = OrderStatus.CANCELLED
            livestock = Livestock.query.get(order.livestock_id)
            if livestock:
                livestock.status = LivestockStatus.AVAILABLE
        elif action == "release_escrow":
            order.status = OrderStatus.DELIVERED
            from app.services.escrow_manager import EscrowManager

            EscrowManager.release_escrow(order.id)

    admin_id = get_jwt_identity()
    audit = AuditLog(
        admin_id=admin_id,
        action="dispute_resolved",
        entity_type="dispute",
        entity_id=dispute_id,
        new_values={"resolution": resolution, "action": action},
    )
    db.session.add(audit)
    db.session.commit()

    return jsonify({
        "message": "Dispute resolved successfully",
        "resolution": resolution,
    }), 200


@admin_bp.route("/orders", methods=["GET"])
@jwt_required()
@admin_required
def get_all_orders():
    """Get all orders on platform."""
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    status = request.args.get("status")

    query = Order.query

    if status:
        query = query.filter_by(status=status)

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


@admin_bp.route("/orders/<int:order_id>", methods=["GET"])
@jwt_required()
@admin_required
def get_order_detail(order_id):
    """Get order details with payment and dispute info."""
    order = Order.query.get(order_id)

    if not order:
        return jsonify({"error": "Order not found"}), 404

    return jsonify({
        "order": order.to_dict(),
        "payment": {
            "status": order.payment.status if order.payment else None,
            "mpesa_receipt": order.payment.mpesa_receipt_number
            if order.payment
            else None,
        }
        if order.payment
        else None,
        "dispute": {
            "id": order.dispute.id,
            "status": order.dispute.status,
            "type": order.dispute.dispute_type,
        }
        if order.dispute
        else None,
    }), 200


@admin_bp.route("/dashboard", methods=["GET"])
@jwt_required()
@admin_required
def get_dashboard():
    """Get admin dashboard metrics."""
    today = datetime.utcnow().date()

    total_users = User.query.count()
    farmers = User.query.filter_by(role=UserRole.FARMER).count()
    buyers = User.query.filter_by(role=UserRole.BUYER).count()
    new_users_today = User.query.filter(func.date(User.created_at) == today).count()

    total_orders = Order.query.count()
    pending_orders = Order.query.filter_by(status=OrderStatus.PENDING).count()
    completed_orders = Order.query.filter_by(status=OrderStatus.DELIVERED).count()

    total_revenue = (
        db.session
        .query(func.sum(Order.total_amount))
        .filter(Order.status == OrderStatus.DELIVERED)
        .scalar()
        or 0
    )

    today_revenue = (
        db.session
        .query(func.sum(Order.total_amount))
        .filter(
            Order.status == OrderStatus.DELIVERED, func.date(Order.placed_at) == today
        )
        .scalar()
        or 0
    )

    total_listings = Livestock.query.count()
    available_listings = Livestock.query.filter_by(
        status=LivestockStatus.AVAILABLE
    ).count()

    open_disputes = Dispute.query.filter_by(status=DisputeStatus.OPEN).count()
    under_review = Dispute.query.filter_by(status=DisputeStatus.UNDER_REVIEW).count()

    return jsonify({
        "users": {
            "total": total_users,
            "farmers": farmers,
            "buyers": buyers,
            "new_today": new_users_today,
        },
        "orders": {
            "total": total_orders,
            "pending": pending_orders,
            "completed": completed_orders,
        },
        "revenue": {"total": float(total_revenue), "today": float(today_revenue)},
        "listings": {"total": total_listings, "available": available_listings},
        "disputes": {"open": open_disputes, "under_review": under_review},
    }), 200


@admin_bp.route("/audit-logs", methods=["GET"])
@jwt_required()
@admin_required
def get_audit_logs():
    """Get admin audit logs."""
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 50, type=int)
    admin_id = request.args.get("admin_id", type=int)
    action = request.args.get("action")

    query = AuditLog.query

    if admin_id:
        query = query.filter_by(admin_id=admin_id)
    if action:
        query = query.filter_by(action=action)

    pagination = query.order_by(AuditLog.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        "logs": [
            {
                "id": log.id,
                "admin_id": log.admin_id,
                "action": log.action,
                "entity_type": log.entity_type,
                "entity_id": log.entity_id,
                "created_at": log.created_at.isoformat(),
            }
            for log in pagination.items
        ],
        "total": pagination.total,
        "page": pagination.page,
        "per_page": pagination.per_page,
        "pages": pagination.pages,
    }), 200


@admin_bp.route("/settings", methods=["GET"])
@jwt_required()
@admin_required
def get_settings():
    """Get system settings."""
    settings = SystemSettings.query.all()

    return jsonify({
        "settings": {setting.key: setting.value for setting in settings}
    }), 200


@admin_bp.route("/settings", methods=["POST"])
@jwt_required()
@admin_required
def update_settings():
    """Update system settings."""
    data = request.get_json()
    admin_id = get_jwt_identity()

    for key, value in data.items():
        setting = SystemSettings.query.filter_by(key=key).first()
        if setting:
            setting.value = str(value)
            setting.updated_by = admin_id
        else:
            setting = SystemSettings(key=key, value=str(value), updated_by=admin_id)
            db.session.add(setting)

    db.session.commit()

    return jsonify({"message": "Settings updated successfully"}), 200
