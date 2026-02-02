"""
Escrow Manager
Background tasks for fund release/timers
"""

from datetime import datetime, timedelta
from app import db
from app.models import Order, EscrowAccount


class EscrowManager:
    """Manager for escrow account operations."""

    RELEASE_DELAY_DAYS = 3

    @classmethod
    def create_escrow(cls, order_id):
        """Create an escrow account for an order."""
        order = Order.query.get(order_id)

        if not order:
            raise ValueError(f"Order {order_id} not found")

        existing = EscrowAccount.query.filter_by(order_id=order_id).first()
        if existing:
            return existing

        farmer_payout = float(order.total_amount) - float(order.commission_amount)

        escrow = EscrowAccount(
            order_id=order_id,
            amount=order.total_amount,
            farmer_payout_amount=farmer_payout,
            status="held",
        )

        db.session.add(escrow)
        db.session.commit()

        return escrow

    @classmethod
    def release_escrow(cls, order_id, early=False):
        """Release escrow funds to farmer."""
        escrow = EscrowAccount.query.filter_by(order_id=order_id).first()

        if not escrow:
            raise ValueError(f"Escrow for order {order_id} not found")

        if escrow.status != "held":
            raise ValueError(f"Escrow is not in held status: {escrow.status}")

        escrow.status = "released"
        escrow.released_at = datetime.utcnow()

        db.session.commit()

        return True

    @classmethod
    def refund_escrow(cls, order_id, reason="Dispute resolution"):
        """Refund escrow to buyer."""
        escrow = EscrowAccount.query.filter_by(order_id=order_id).first()

        if not escrow:
            raise ValueError(f"Escrow for order {order_id} not found")

        if escrow.status != "held":
            raise ValueError(f"Escrow is not in held status: {escrow.status}")

        escrow.status = "refunded"
        db.session.commit()

        return True

    @classmethod
    def check_and_release_expired(cls):
        """Check for expired escrow accounts and release them."""
        release_date = datetime.utcnow() - timedelta(days=cls.RELEASE_DELAY_DAYS)

        expired_escrows = EscrowAccount.query.filter(
            EscrowAccount.status == "held", EscrowAccount.held_at <= release_date
        ).all()

        released_count = 0
        for escrow in expired_escrows:
            try:
                cls.release_escrow(escrow.order_id, early=False)
                released_count += 1
            except Exception as e:
                print(f"Failed to release escrow {escrow.order_id}: {str(e)}")

        return released_count

    @classmethod
    def get_escrow_status(cls, order_id):
        """Get escrow status for an order."""
        escrow = EscrowAccount.query.filter_by(order_id=order_id).first()

        if not escrow:
            return {"order_id": order_id, "status": "not_created"}

        return {
            "order_id": order_id,
            "status": escrow.status,
            "amount": float(escrow.amount),
            "farmer_payout": float(escrow.farmer_payout_amount),
            "held_at": escrow.held_at.isoformat(),
            "released_at": escrow.released_at.isoformat()
            if escrow.released_at
            else None,
        }
