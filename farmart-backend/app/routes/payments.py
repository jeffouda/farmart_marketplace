from flask import Blueprint, request, jsonify
from app.services.mpesa_service import send_stk_push

payments_bp = Blueprint('payments', __name__)