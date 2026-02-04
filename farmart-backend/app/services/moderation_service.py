"""
Moderation Service
Admin actions around disputes, escrow release, and refunds.
Python 3.8 compatible (no `str | None` syntax).
"""

from datetime import datetime
from typing import Optional

from app import db
from app.models import (
    Dispute,
    DisputeStatus,
    Order,
    OrderStatus,
    Livestock,
    LivestockStatus,
    Payment,
    PaymentStatus,
)
from app.services.escrow_manager import EscrowManager


class ModerationService:
    """Business logic for admin moderation decisions."""

    @staticmethod
    def mark_under_review(dispute: Dispute, admin_notes: Optional[str] = None) -> Dispute:
        """Move a dispute to UNDER_REVIEW."""
        if not dispute:
            raise ValueError("Dispute is required")

        if dispute.status != DisputeStatus.OPEN:
            raise ValueError(f"Dispute must be OPEN to move under review (got '{dispute.status}')")

        dispute.status = DisputeStatus.UNDER_REVIEW
        if admin_notes:
            dispute.admin_notes = admin_notes

        db.session.commit()
        return dispute

    @staticmethod
    def release_escrow(order_id: int) -> bool:
        """
        Release escrow funds for an order.
        Typically used when admin decides the farmer should be paid.
        """
        order = Order.query.get(order_id)
        if not order:
            raise ValueError(f"Order {order_id} not found")

        # Release escrow
        EscrowManager.release_escrow(order_id)

        # Mark payment as completed (optional but useful)
        payment = Payment.query.filter_by(order_id=order_id).first()
        if payment and payment.status != PaymentStatus.COMPLETED:
            payment.status = PaymentStatus.COMPLETED
            payment.payment_date = datetime.utcnow()

        db.session.commit()
        return True

    @staticmethod
    def refund_order(order_id: int, refund_amount: Optional[float] = None) -> bool:
        """
        Refund escrow funds to buyer (full or partial).
        Also updates payment/order status appropriately.
        """
        order = Order.query.get(order_id)
        if not order:
            raise ValueError(f"Order {order_id} not found")

        # Refund escrow (escrow_manager refunds whole "held" amount logically)
        EscrowManager.refund_escrow(order_id, reason="Admin dispute resolution")

        # Update payment record (best-effort bookkeeping)
        payment = Payment.query.filter_by(order_id=order_id).first()
        if payment:
            payment.status = PaymentStatus.REFUNDED
            payment.payment_date = datetime.utcnow()

        # Update order + relist livestock
        order.status = OrderStatus.CANCELLED
        order.cancelled_at = datetime.utcnow()
        if refund_amount is not None:
            order.cancellation_reason = f"Refunded KES {refund_amount} after dispute resolution"
        else:
            order.cancellation_reason = "Refunded after dispute resolution"

        livestock = Livestock.query.get(order.livestock_id)
        if livestock:
            livestock.status = LivestockStatus.AVAILABLE

        db.session.commit()
        return True


# exported instance (matches your admin.py import)
moderation_service = ModerationService()
