"""
Authentication Routes using Flask-RESTful
Provides RESTful API endpoints for authentication
"""

from flask import Blueprint, request, make_response
from flask_restful import Api, Resource
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    set_access_cookies,
    set_refresh_cookies,
    unset_jwt_cookies,
)
from app import db
from app.models import User
from app.schemas import user_register_schema, user_login_schema, user_schema
from app.extensions import limiter

import re  # For XSS prevention

# Blueprint for backward compatibility
auth_bp = Blueprint("auth", __name__)
auth_api = Api(auth_bp)


# Custom error handler for rate limiting
@auth_bp.errorhandler(429)
def ratelimit_handler(e):
    return {
        "error": "Too many attempts. Please try again in 5 minutes.",
        "code": "RATE_LIMIT",
    }, 429


class AuthRegister(Resource):
    """Resource for user registration."""

    method_decorators = []
    if limiter:
        method_decorators = [limiter.limit("5 per minute")]

    def strip_html_tags(self, text):
        """Strip HTML/script tags to prevent Stored XSS attacks."""
        if not text:
            return text
        # Remove HTML tags
        clean = re.sub(r"<[^>]*>", "", str(text))
        # Remove script tag patterns
        clean = re.sub(r"<script[^>]*>[^<]*</script>", "", clean, flags=re.IGNORECASE)
        # Remove JavaScript event handlers
        clean = re.sub(r'on\w+="[^"]*"', "", clean)
        clean = re.sub(r"on\w+='[^']*'", "", clean)
        return clean.strip()

    def post(self):
        """Register a new user."""
        # Validate input using marshmallow schema
        try:
            data = user_register_schema.load(request.get_json())
        except Exception as err:
            return {"error": err.messages}, 400

        # Sanity Check: Strip HTML/script tags from usernames (XSS Prevention)
        data["first_name"] = self.strip_html_tags(data.get("first_name", ""))
        data["last_name"] = self.strip_html_tags(data.get("last_name", ""))

        # Check if user already exists
        if User.query.filter_by(email=data["email"]).first():
            return {"error": "Email already registered"}, 400

        # Check if phone number already exists
        if User.query.filter_by(phone_number=data["phone_number"]).first():
            return {"error": "Phone number already registered"}, 400

        # Create new user
        user = User(
            email=data["email"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            phone_number=data["phone_number"],
            role=data["role"],
            is_verified=True,  # Auto-verify for development/demo
        )
        user.set_password(data["password"])

        db.session.add(user)
        db.session.commit()

        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)

        # Set JWT tokens as HttpOnly, Secure cookies
        response = make_response(
            {
                "message": "User registered successfully",
                "user": user_schema.dump(user),
            },
            201,
        )
        set_access_cookies(response, access_token)
        set_refresh_cookies(response, refresh_token)

        return response


class AuthLogin(Resource):
    """Resource for user login."""

    method_decorators = []
    if limiter:
        method_decorators = [limiter.limit("5 per minute")]

    def post(self):
        """Login user and return JWT tokens via secure cookies."""
        try:
            data = user_login_schema.load(request.get_json())
        except Exception as err:
            return {"error": err.messages}, 400

        user = User.query.filter_by(email=data["email"]).first()

        # Prevent user enumeration
        if not user or not user.check_password(data["password"]):
            return {"error": "Invalid email or password"}, 401

        if not user.is_verified:
            return {"error": "Please verify your email first"}, 403

        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)

        response = make_response(
            {
                "message": "Login successful",
                "user": user_schema.dump(user),
            },
            200,
        )
        set_access_cookies(response, access_token)
        set_refresh_cookies(response, refresh_token)

        return response


class AuthLogout(Resource):
    """Resource for user logout."""

    @jwt_required()
    def post(self):
        """Logout user and clear secure cookies."""
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        response = make_response(
            {
                "message": "Logged out successfully",
                "user": user_schema.dump(user) if user else None,
            },
            200,
        )
        unset_jwt_cookies(response)

        return response


class AuthRefresh(Resource):
    """Resource for token refresh."""

    @jwt_required(refresh=True)
    def post(self):
        current_user_id = get_jwt_identity()
        access_token = create_access_token(identity=current_user_id)
        return {"access_token": access_token}, 200


class AuthMe(Resource):
    """Resource for getting current user."""

    @jwt_required()
    def get(self):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return {"error": "User not found"}, 404

        return {"user": user_schema.dump(user)}, 200


class AuthProfile(Resource):
    """Resource for updating user profile."""

    @jwt_required()
    def patch(self):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return {"error": "User not found"}, 404

        data = request.get_json() or {}

        # Handle profile image removal
        if data.get("profile_image_url") is None:
            user.profile_image_url = None
            if user.profile:
                user.profile.profile_image_url = None

        # Update other fields
        for field in [
            "first_name",
            "last_name",
            "phone_number",
            "location",
            "bio",
            "farm_name",
            "farm_location",
            "specialization",
        ]:
            if field in data:
                setattr(user, field, data[field])
                if user.profile:
                    setattr(user.profile, field, data[field])

        db.session.commit()

        return {
            "message": "Profile updated successfully",
            "user": user_schema.dump(user),
        }, 200


# Register resources with the API
auth_api.add_resource(AuthRegister, "/register")
auth_api.add_resource(AuthLogin, "/login")
auth_api.add_resource(AuthLogout, "/logout")
auth_api.add_resource(AuthRefresh, "/refresh")
auth_api.add_resource(AuthMe, "/me")
auth_api.add_resource(AuthProfile, "/profile")
