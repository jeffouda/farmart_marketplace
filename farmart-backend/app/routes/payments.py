from flask import Blueprint, request, jsonify
from app.services.mpesa_service import send_stk_push

payments_bp = Blueprint('payments', __name__)

@payments_bp.route('/stk-push', methods=['POST'])
def trigger_stk():
    data = request.get_json()
    phone = data.get('phoneNumber')
    amount = data.get('amount', 1)

    if not phone:
        return jsonify({"error": "Phone number is required"}), 

    result = send_stk_push(phone, amount)

    if "ResponseCode" in result and result["ResponseCode"] == "0":
        return jsonify({"status": "success", "data": result}), 200
    else:
        return jsonify({"status": "error", "message": result}), 400
    