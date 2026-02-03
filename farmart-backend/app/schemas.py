"""
Marshmallow Schemas for FarmAT API
Provides model-level validation and serialization for API responses
"""

from flask_marshmallow import Marshmallow
from marshmallow import validate, fields, validates, ValidationError
from app.extensions import db

ma = Marshmallow()


class UserSchema(ma.SQLAlchemyAutoSchema):
    """Marshmallow schema for User model with validation."""

    class Meta:
        load_instance = True
        sqla_session = db.session

    id = fields.Integer(dump_only=True)
    email = fields.Email(required=True, validate=validate.Length(max=255))
    first_name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    last_name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    phone_number = fields.String(
        required=True, validate=validate.Length(min=10, max=20)
    )
    role = fields.String(
        required=True, validate=validate.OneOf(["farmer", "buyer", "admin"])
    )
    is_active = fields.Boolean(dump_only=True)
    is_verified = fields.Boolean(dump_only=True)
    created_at = fields.DateTime(dump_only=True)


class UserRegisterSchema(ma.Schema):
    """Schema for user registration with password validation."""

    email = fields.Email(required=True)
    password = fields.String(
        required=True,
        validate=[
            validate.Length(min=8),
            validate.Regexp(
                r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]+$",
                error="Password must contain uppercase, lowercase, digit, and special character",
            ),
        ],
    )
    first_name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    last_name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    phone_number = fields.String(
        required=True, validate=validate.Length(min=10, max=20)
    )
    role = fields.String(
        required=True, validate=validate.OneOf(["farmer", "buyer", "admin"])
    )


class UserLoginSchema(ma.Schema):
    """Schema for user login."""

    email = fields.Email(required=True)
    password = fields.String(required=True)


class LivestockSchema(ma.SQLAlchemyAutoSchema):
    """Marshmallow schema for Livestock model with validation."""

    class Meta:
        load_instance = True
        sqla_session = db.session

    id = fields.Integer(dump_only=True)
    farmer_id = fields.Integer(required=True)
    name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    species = fields.String(
        required=True,
        validate=validate.OneOf([
            "cattle",
            "goats",
            "sheep",
            "pigs",
            "chickens",
            "other",
        ]),
    )
    breed = fields.String(validate=validate.Length(max=100))
    gender = fields.String(validate=validate.OneOf(["male", "female"]))
    age_years = fields.Float(validate=validate.Range(min=0))
    age_months = fields.Integer(validate=validate.Range(min=0))
    weight_kg = fields.Float(validate=validate.Range(min=0))
    color = fields.String(validate=validate.Length(max=50))
    description = fields.String()
    health_status = fields.String(validate=validate.Length(max=50))
    price = fields.Decimal(
        required=True, validate=validate.Range(min=0), as_string=True
    )
    currency = fields.String(validate=validate.Length(max=3))
    status = fields.String(
        validate=validate.OneOf(["available", "sold", "reserved", "pending_approval"])
    )
    view_count = fields.Integer(dump_only=True)
    created_at = fields.DateTime(dump_only=True)


class OrderSchema(ma.SQLAlchemyAutoSchema):
    """Marshmallow schema for Order model with validation."""

    class Meta:
        load_instance = True
        sqla_session = db.session

    id = fields.Integer(dump_only=True)
    order_number = fields.String(dump_only=True)
    buyer_id = fields.Integer(required=True)
    livestock_id = fields.Integer(required=True)
    quantity = fields.Integer(load_default=1, validate=validate.Range(min=1))
    unit_price = fields.Decimal(
        required=True, validate=validate.Range(min=0), as_string=True
    )
    subtotal = fields.Decimal(
        required=True, validate=validate.Range(min=0), as_string=True
    )
    commission_amount = fields.Decimal(
        required=True, validate=validate.Range(min=0), as_string=True
    )
    total_amount = fields.Decimal(
        required=True, validate=validate.Range(min=0), as_string=True
    )
    status = fields.String(
        validate=validate.OneOf([
            "pending",
            "confirmed",
            "processing",
            "shipped",
            "delivered",
            "cancelled",
            "dispute",
        ])
    )
    shipping_address = fields.String(required=True)
    buyer_notes = fields.String()
    placed_at = fields.DateTime(dump_only=True)
    confirmed_at = fields.DateTime(dump_only=True)
    shipped_at = fields.DateTime(dump_only=True)
    delivered_at = fields.DateTime(dump_only=True)


class PaymentSchema(ma.SQLAlchemyAutoSchema):
    """Marshmallow schema for Payment model with validation."""

    class Meta:
        load_instance = True
        sqla_session = db.session

    id = fields.Integer(dump_only=True)
    order_id = fields.Integer(required=True)
    amount = fields.Decimal(
        required=True, validate=validate.Range(min=0), as_string=True
    )
    currency = fields.String(validate=validate.Length(max=3))
    payment_method = fields.String(validate=validate.OneOf(["mpesa", "bank", "card"]))
    mpesa_transaction_id = fields.String(dump_only=True)
    mpesa_receipt_number = fields.String(dump_only=True)
    status = fields.String(
        validate=validate.OneOf([
            "pending",
            "processing",
            "completed",
            "failed",
            "refunded",
        ])
    )
    payment_date = fields.DateTime()
    created_at = fields.DateTime(dump_only=True)


class DisputeSchema(ma.SQLAlchemyAutoSchema):
    """Marshmallow schema for Dispute model with validation."""

    class Meta:
        load_instance = True
        sqla_session = db.session

    id = fields.Integer(dump_only=True)
    order_id = fields.Integer(required=True)
    dispute_type = fields.String(
        required=True,
        validate=validate.OneOf(["quality", "delivery", "payment", "other"]),
    )
    description = fields.String(required=True)
    evidence_urls = fields.String()
    status = fields.String(
        validate=validate.OneOf(["open", "under_review", "resolved", "closed"])
    )
    admin_notes = fields.String()
    resolution = fields.String()
    amount_refunded = fields.Decimal(validate=validate.Range(min=0), as_string=True)
    opened_at = fields.DateTime(dump_only=True)
    resolved_at = fields.DateTime(dump_only=True)


# Schema instances for use in routes
user_schema = UserSchema()
users_schema = UserSchema(many=True)
user_register_schema = UserRegisterSchema()
user_login_schema = UserLoginSchema()
livestock_schema = LivestockSchema()
livestock_list_schema = LivestockSchema(many=True)
order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)
payment_schema = PaymentSchema()
payments_schema = PaymentSchema(many=True)
dispute_schema = DisputeSchema()
disputes_schema = DisputeSchema(many=True)
