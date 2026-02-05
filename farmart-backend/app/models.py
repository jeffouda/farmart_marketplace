"""
SQLAlchemy Models for FarmAT Database
Based on the DBML schema definition
"""

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token
from app.extensions import db


# Enum-like classes for fixed choices
class UserRole:
    FARMER = "farmer"
    BUYER = "buyer"
    ADMIN = "admin"


class LivestockStatus:
    AVAILABLE = "available"
    SOLD = "sold"
    RESERVED = "reserved"
    PENDING_APPROVAL = "pending_approval"


class OrderStatus:
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    DISPUTE = "dispute"


class PaymentStatus:
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class DisputeStatus:
    OPEN = "open"
    UNDER_REVIEW = "under_review"
    RESOLVED = "resolved"
    CLOSED = "closed"


# ==================== User Models ====================


class User(db.Model):
    """Base user model with authentication and profile."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False, default=UserRole.BUYER)
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    profile = db.relationship("UserProfile", back_populates="user", uselist=False)
    livestock = db.relationship(
        "Livestock", back_populates="farmer", foreign_keys="Livestock.farmer_id"
    )
    orders = db.relationship(
        "Order", back_populates="buyer", foreign_keys="Order.buyer_id"
    )
    payments = db.relationship("Payment", back_populates="user")
    addresses = db.relationship("UserAddress", back_populates="user")

    def set_password(self, password):
        """Hash and set user password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify user password."""
        return check_password_hash(self.password_hash, password)

    def get_tokens(self):
        """Generate JWT access and refresh tokens."""
        access_token = create_access_token(
            identity=self.id, additional_claims={"role": self.role}
        )
        refresh_token = create_refresh_token(identity=self.id)
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 86400,  # 24 hours
        }

    def to_dict(self):
        """Convert user to dictionary."""
        return {
            "id": self.id,
            "email": self.email,
            "phone_number": self.phone_number,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "role": self.role,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class UserProfile(db.Model):
    """Extended user profile information."""

    __tablename__ = "user_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False
    )
    bio = db.Column(db.Text)
    profile_image_url = db.Column(db.String(500))
    id_number = db.Column(db.String(50))
    id_image_front = db.Column(db.String(500))
    id_image_back = db.Column(db.String(500))
    location = db.Column(db.String(255))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    bank_name = db.Column(db.String(100))
    bank_account_number = db.Column(db.String(50))
    mpesa_number = db.Column(db.String(20))
    is_verified = db.Column(db.Boolean, default=False)
    rating = db.Column(db.Float, default=0.0)
    total_sales = db.Column(db.Integer, default=0)
    total_purchases = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    user = db.relationship("User", back_populates="profile")


class UserAddress(db.Model):
    """User saved addresses for delivery."""

    __tablename__ = "user_addresses"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    label = db.Column(db.String(50))  # e.g., "Home", "Office"
    recipient_name = db.Column(db.String(100), nullable=False)
    recipient_phone = db.Column(db.String(20), nullable=False)
    street_address = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    county = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="addresses")


# ==================== Livestock Models ====================


class Vaccination(db.Model):
    """Vaccination records for livestock."""

    __tablename__ = "vaccinations"

    id = db.Column(db.Integer, primary_key=True)
    livestock_id = db.Column(db.Integer, db.ForeignKey("livestock.id"), nullable=False)

    name = db.Column(
        db.String(100), nullable=False
    )  # e.g., Foot and Mouth, Brucellosis
    date_administered = db.Column(db.Date, nullable=False)
    next_due_date = db.Column(db.Date)
    certificate_url = db.Column(db.String(500))  # URL to vaccine certificate
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    livestock = db.relationship("Livestock", back_populates="vaccinations")

    def to_dict(self):
        return {
            "id": self.id,
            "livestock_id": self.livestock_id,
            "name": self.name,
            "date_administered": self.date_administered.isoformat()
            if self.date_administered
            else None,
            "next_due_date": self.next_due_date.isoformat()
            if self.next_due_date
            else None,
            "certificate_url": self.certificate_url,
        }


class Livestock(db.Model):
    __tablename__ = "livestock"

    id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    animal_type = db.Column(db.String(50), nullable=False)  # Cow, Goat, Sheep
    breed = db.Column(db.String(100))
    gender = db.Column(db.String(20))  # male, female
    weight = db.Column(db.Float, nullable=False)
    age_months = db.Column(db.Integer)
    price = db.Column(db.Float, nullable=False)
    price_per_kg = db.Column(db.Float)  # Optional: price per kg
    original_price = db.Column(db.Float)  # Original price for showing discounts
    location = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(500))  # Primary image URL
    images = db.Column(db.Text)  # JSON array of additional image URLs

    description = db.Column(db.Text)  # Selling pitch / reason for sale
    reason_for_sale = db.Column(db.String(100))  # Breeding, Slaughter, Dairy, etc.
    health_certified = db.Column(db.Boolean, default=False)

    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    farmer = db.relationship("User", back_populates="livestock")
    orders = db.relationship("Order", back_populates="livestock")
    vaccinations = db.relationship(
        "Vaccination", back_populates="livestock", cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "animal_type": self.animal_type,
            "breed": self.breed,
            "gender": self.gender,
            "weight": self.weight,
            "age_months": self.age_months,
            "price": float(self.price),
            "price_per_kg": float(self.price_per_kg) if self.price_per_kg else None,
            "location": self.location,
            "image_url": self.image_url,
            "images": self.images.split(",") if self.images else [],
            "description": self.description,
            "reason_for_sale": self.reason_for_sale,
            "health_certified": self.health_certified,
            "is_available": self.is_available,
            "vaccinations": [v.to_dict() for v in self.vaccinations]
            if self.vaccinations
            else [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# ==================== Order Models ====================


class Order(db.Model):
    """Customer orders for livestock."""

    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    buyer_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True
    )
    livestock_id = db.Column(db.Integer, db.ForeignKey("livestock.id"), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    commission_rate = db.Column(db.Float, default=0.02)  # 2% commission
    commission_amount = db.Column(db.Numeric(10, 2), nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(30), default=OrderStatus.PENDING)
    shipping_address = db.Column(db.Text, nullable=False)
    buyer_notes = db.Column(db.Text)
    placed_at = db.Column(db.DateTime, default=datetime.utcnow)
    confirmed_at = db.Column(db.DateTime)
    shipped_at = db.Column(db.DateTime)
    delivered_at = db.Column(db.DateTime)
    cancelled_at = db.Column(db.DateTime)
    cancellation_reason = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    buyer = db.relationship("User", back_populates="orders", foreign_keys=[buyer_id])
    livestock = db.relationship("Livestock", back_populates="orders")
    payment = db.relationship("Payment", back_populates="order", uselist=False)
    dispute = db.relationship("Dispute", back_populates="order", uselist=False)

    def to_dict(self):
        """Convert order to dictionary."""
        return {
            "id": self.id,
            "order_number": self.order_number,
            "buyer_id": self.buyer_id,
            "livestock_id": self.livestock_id,
            "livestock": self.livestock.to_dict() if self.livestock else None,
            "quantity": self.quantity,
            "unit_price": float(self.unit_price),
            "subtotal": float(self.subtotal),
            "commission_amount": float(self.commission_amount),
            "total_amount": float(self.total_amount),
            "status": self.status,
            "shipping_address": self.shipping_address,
            "placed_at": self.placed_at.isoformat() if self.placed_at else None,
        }


# ==================== Payment Models ====================


class Payment(db.Model):
    """Payment records for orders."""

    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(
        db.Integer, db.ForeignKey("orders.id"), unique=True, nullable=False
    )
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), default="KES")
    payment_method = db.Column(db.String(50))  # mpesa, bank, card
    mpesa_transaction_id = db.Column(db.String(100))
    mpesa_receipt_number = db.Column(db.String(100))
    merchant_request_id = db.Column(db.String(100))
    checkout_request_id = db.Column(db.String(100))
    status = db.Column(db.String(30), default=PaymentStatus.PENDING)
    payment_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    order = db.relationship("Order", back_populates="payment")
    user = db.relationship("User", back_populates="payments")


class EscrowAccount(db.Model):
    """Escrow account for holding funds during transactions."""

    __tablename__ = "escrow_accounts"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(
        db.Integer, db.ForeignKey("orders.id"), unique=True, nullable=False
    )
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    farmer_payout_amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(30), default="held")  # held, released, refunded
    held_at = db.Column(db.DateTime, default=datetime.utcnow)
    released_at = db.Column(db.DateTime)
    release_conditions = db.Column(db.Text)  # JSON conditions for release
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ==================== Dispute Models ====================


class Dispute(db.Model):
    """Dispute records for orders."""

    __tablename__ = "disputes"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(
        db.Integer, db.ForeignKey("orders.id"), unique=True, nullable=False
    )
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    dispute_type = db.Column(
        db.String(50), nullable=False
    )  # quality, delivery, payment, other
    description = db.Column(db.Text, nullable=False)
    evidence_urls = db.Column(db.Text)  # JSON array of evidence URLs
    status = db.Column(db.String(30), default=DisputeStatus.OPEN)
    admin_notes = db.Column(db.Text)
    resolution = db.Column(db.Text)
    amount_refunded = db.Column(db.Numeric(10, 2))
    opened_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    order = db.relationship("Order", back_populates="dispute")
    user = db.relationship("User", foreign_keys=[user_id])


# ==================== Admin Models ====================


class CommissionRule(db.Model):
    """Commission rules for different categories/conditions."""

    __tablename__ = "commission_rules"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))  # species, user_tier, order_value
    min_order_value = db.Column(db.Numeric(10, 2))
    max_order_value = db.Column(db.Numeric(10, 2))
    commission_rate = db.Column(db.Float, nullable=False)  # percentage as decimal
    is_active = db.Column(db.Boolean, default=True)
    effective_from = db.Column(db.Date)
    effective_to = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class AuditLog(db.Model):
    """Audit log for admin actions."""

    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    entity_type = db.Column(db.String(50))  # user, order, livestock, payment
    entity_id = db.Column(db.Integer)
    old_values = db.Column(db.Text)  # JSON
    new_values = db.Column(db.Text)  # JSON
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    admin = db.relationship("User", foreign_keys=[admin_id])


class SystemSettings(db.Model):
    """System-wide settings managed by admin."""

    __tablename__ = "system_settings"

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    updated_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


# ==================== Analytics Models ====================


class AnalyticsEvent(db.Model):
    """Analytics events for tracking platform activity."""

    __tablename__ = "analytics_events"

    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(
        db.String(50), nullable=False
    )  # page_view, search, listing_view
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    session_id = db.Column(db.String(100))
    entity_type = db.Column(db.String(50))
    entity_id = db.Column(db.Integer)
    event_metadata = db.Column(db.Text)  # JSON
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", foreign_keys=[user_id])


class DailyMetrics(db.Model):
    """Daily aggregated metrics."""

    __tablename__ = "daily_metrics"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, index=True)
    total_listings = db.Column(db.Integer, default=0)
    total_orders = db.Column(db.Integer, default=0)
    total_revenue = db.Column(db.Numeric(12, 2), default=0)
    total_commission = db.Column(db.Numeric(12, 2), default=0)
    new_users = db.Column(db.Integer, default=0)
    active_users = db.Column(db.Integer, default=0)
    page_views = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

