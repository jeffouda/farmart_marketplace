"""
Input Validation Utilities
Provides validation functions for user input
"""

import re
from flask import jsonify


def validate_email(email):
    """Validate email format."""
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(pattern, email) is not None


def validate_password(password):
    """
    Validate password strength.
    Requirements:
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit"
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain at least one special character"
    return True, "Password is valid"


def validate_phone(phone):
    """Validate phone number format (Kenyan format)."""
    # Remove any spaces or dashes
    phone = re.sub(r"[\s-]", "", phone)
    # Kenyan phone numbers: 07XX XXX XXX or 254XXXXXXXXX
    pattern = r"^(07\d{8}|254\d{9})$"
    return re.match(pattern, phone) is not None


def validate_required_fields(data, required_fields):
    """Check if all required fields are present in data."""
    missing_fields = []
    for field in required_fields:
        if field not in data or data[field] is None or data[field] == "":
            missing_fields.append(field)
    return missing_fields


def validate_livestock_data(data):
    """Validate livestock listing data."""
    errors = []

    if "name" not in data or not data["name"]:
        errors.append("Livestock name is required")
    if "species" not in data or not data["species"]:
        errors.append("Species is required")
    if "price" not in data or not data["price"]:
        errors.append("Price is required")
    elif float(data["price"]) <= 0:
        errors.append("Price must be greater than 0")

    return errors


def validate_order_data(data):
    """Validate order creation data."""
    errors = []

    if "livestock_id" not in data:
        errors.append("Livestock ID is required")
    if "shipping_address" not in data or not data["shipping_address"]:
        errors.append("Shipping address is required")

    return errors
