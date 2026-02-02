"""
Payment Routes
M-Pesa STK Push & Daraja Callbacks
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app.models import Order, Payment, User, EscrowAccount, Livestock
from app import db
from app.services.mpesa_service import MpesaService
from app.services.escrow_manager import EscrowManager

payments_bp = Blueprint("payments", __name__)


@payments_bp.route("/initiate", methods=["POST"])
@jwt_required()
def initiate_payment():
    """
    Initiate M-Pesa STK Push for an order.

    Request body:
        - order_id: Order ID to pay for
    """
    current_user_id = get_jwt_identity()
    data = request.get_json()

    order_id = data.get("order_id")
    if not order_id:
        return jsonify({"error": "Order ID is required"}), 400

    order = Order.query.filter_by(id=order_id, buyer_id=current_user_id).first()

    if not order:
        return jsonify({"error": "Order not found"}), 404

    if order.status not in ["pending", "confirmed"]:
        return jsonify({"error": "Order is not in a payable state"}), 400

    # Check if payment already exists
    existing_payment = Payment.query.filter_by(order_id=order_id).first()
    if existing_payment and existing_payment.status == "completed":
        return jsonify({"error": "Order has already been paid"}), 400

    user = User.query.get(current_user_id)

    try:
        # Initiate M-Pesa STK Push
        result = MpesaService.initiate_stk_push(
            phone_number=user.phone_number,
            amount=int(order.total_amount),
            account_reference=order.order_number,
            transaction_desc=f"Payment for order {order.order_number}",
        )

        # Create or update payment record
        if existing_payment:
            existing_payment.merchant_request_id = result.get("MerchantRequestID")
            existing_payment.checkout_request_id = result.get("CheckoutRequestID")
            existing_payment.status = "processing"
            payment = existing_payment
        else:
            payment = Payment(
                order_id=order_id,
                user_id=current_user_id,
                amount=order.total_amount,
                payment_method="mpesa",
                merchant_request_id=result.get("MerchantRequestID"),
                checkout_request_id=result.get("CheckoutRequestID"),
                status="processing",
            )
            db.session.add(payment)

        db.session.commit()

        return jsonify({
            "message": "STK Push initiated successfully",
            "merchant_request_id": result.get("MerchantRequestID"),
            "checkout_request_id": result.get("CheckoutRequestID"),
            "response_code": result.get("ResponseCode"),
            "response_description": result.get("ResponseDescription"),
        }), 200

    except Exception as e:
        return jsonify({"error": f"Payment initiation failed: {str(e)}"}), 500


@payments_bp.route("/callback/mpesa", methods=["POST"])
def mpesa_callback():
    """
    M-Pesa Daraja callback URL for STK Push results.
    """
    try:
        data = request.get_json()

        # Extract callback data
        result_code = data.get("Body", {}).get("stkCallback", {}).get("ResultCode")
        result_desc = data.get("Body", {}).get("stkCallback", {}).get("ResultDesc")
        merchant_request_id = (
            data.get("Body", {}).get("stkCallback", {}).get("MerchantRequestID")
        )
        checkout_request_id = (
            data.get("Body", {}).get("stkCallback", {}).get("CheckoutRequestID")
        )

        # Find payment record
        payment = Payment.query.filter_by(
            merchant_request_id=merchant_request_id
        ).first()

        if not payment:
            return jsonify({"error": "Payment not found"}), 404

        if result_code == 0:
            # Success - extract transaction details
            callback_metadata = (
                data.get("Body", {}).get("stkCallback", {}).get("CallbackMetadata", {})
            )
            items = callback_metadata.get("Item", [])

            mpesa_receipt = None
            transaction_date = None
            phone = None

            for item in items:
                if item.get("Name") == "MpesaReceiptNumber":
                    mpesa_receipt = item.get("Value")
                elif item.get("Name") == "TransactionDate":
                    transaction_date = item.get("Value")
                elif item.get("Name") == "PhoneNumber":
                    phone = item.get("Value")

            # Update payment
            payment.mpesa_receipt_number = mpesa_receipt
            payment.mpesa_transaction_id = (
                f"{merchant_request_id}_{checkout_request_id}"
            )
            payment.status = "completed"
            payment.payment_date = datetime.utcnow()

            # Update order status
            order = Order.query.get(payment.order_id)
            if order and order.status == "pending":
                order.status = "confirmed"
                order.confirmed_at = datetime.utcnow()

                # Create escrow account
                EscrowManager.create_escrow(order.id)

            db.session.commit()

            return jsonify({
                "message": "Payment processed successfully",
                "mpesa_receipt": mpesa_receipt,
            }), 200
        else:
            # Failed
            payment.status = "failed"
            db.session.commit()

            return jsonify({
                "error": "Payment failed",
                "result_code": result_code,
                "result_desc": result_desc,
            }), 400

    except Exception as e:
        return jsonify({"error": f"Callback processing failed: {str(e)}"}), 500


@payments_bp.route("/b2c/callback", methods=["POST"])
def mpesa_b2c_callback():
    """
    M-Pesa B2C callback for payouts to farmers.
    """
    try:
        data = request.get_json()

        # Extract B2C result
        result_code = data.get("Result", {}).get("ResultCode")
        result_desc = data.get("Result", {}).get("ResultDesc")
        transaction_id = data.get("Result", {}).get("TransactionID")
        transaction_amount = data.get("Result", {}).get("TransactionAmount")
        recipient_phone = data.get("Result", {}).get("PartyB")

        if result_code == 0:
            return jsonify({
                "message": "B2C payment processed successfully",
                "transaction_id": transaction_id,
            }), 200
        else:
            return jsonify({
                "error": "B2C payment failed",
                "result_desc": result_desc,
            }), 400

    except Exception as e:
        return jsonify({"error": f"B2C callback failed: {str(e)}"}), 500


@payments_bp.route("/status/<int:order_id>", methods=["GET"])
@jwt_required()
def get_payment_status(order_id):
    """Get payment status for an order."""
    current_user_id = get_jwt_identity()

    order = Order.query.filter_by(id=order_id).first()

    if not order:
        return jsonify({"error": "Order not found"}), 404

    # Check authorization
    if order.buyer_id != current_user_id:
        farmer = User.query.get(order.livestock.farmer_id) if order.livestock else None
        if not farmer or farmer.id != current_user_id:
            return jsonify({"error": "Not authorized"}), 403

    payment = Payment.query.filter_by(order_id=order_id).first()

    if not payment:
        return jsonify({
            "order_id": order_id,
            "payment_status": "not_initiated",
            "order_status": order.status,
        }), 200

    return jsonify({
        "order_id": order_id,
        "payment_status": payment.status,
        "amount": float(payment.amount),
        "mpesa_receipt": payment.mpesa_receipt_number,
        "payment_date": payment.payment_date.isoformat()
        if payment.payment_date
        else None,
        "order_status": order.status,
    }), 200


@payments_bp.route("/query/<int:order_id>", methods=["POST"])
@jwt_required()
def query_payment_status(order_id):
    """Query M-Pesa for payment status."""
    current_user_id = get_jwt_identity()

    payment = Payment.query.filter_by(order_id=order_id).first()

    if not payment:
        return jsonify({"error": "Payment not found"}), 404

    if not payment.checkout_request_id:
        return jsonify({"error": "No checkout request ID"}), 400

    try:
        result = MpesaService.query_stk_status(payment.checkout_request_id)

        return jsonify({
            "result_code": result.get("ResultCode"),
            "result_desc": result.get("ResultDesc"),
            "response_code": result.get("ResponseCode"),
            "response_description": result.get("ResponseDescription"),
        }), 200

    except Exception as e:
        return jsonify({"error": f"Query failed: {str(e)}"}), 500


@payments_bp.route("/refund", methods=["POST"])
@jwt_required()
def refund_payment():
    """Process a refund (admin or system initiated)."""
    from app.utils.decorators import admin_required
    from app.models import OrderStatus

    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    # Only admins can process refunds
    if user.role != "admin":
        return jsonify({"error": "Only admins can process refunds"}), 403

    data = request.get_json()
    order_id = data.get("order_id")

    if not order_id:
        return jsonify({"error": "Order ID is required"}), 400

    payment = Payment.query.filter_by(order_id=order_id).first()

    if not payment:
        return jsonify({"error": "Payment not found"}), 404

    if payment.status != "completed":
        return jsonify({"error": "Payment cannot be refunded"}), 400

    # Here you would implement actual refund logic via M-Pesa B2C
    # For now, mark as refunded
    payment.status = "refunded"

    order = Order.query.get(order_id)
    if order:
        order.status = OrderStatus.CANCELLED

        # Release livestock
        from app.models import LivestockStatus

        livestock = Livestock.query.get(order.livestock_id)
        if livestock:
            livestock.status = LivestockStatus.AVAILABLE

    db.session.commit()

    return jsonify({
        "message": "Refund processed successfully",
        "refund_amount": float(payment.amount),
    }), 200
