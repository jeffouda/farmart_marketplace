"""
Authentication Routes using Flask-RESTful
Provides RESTful API endpoints for authentication
"""

from flask import Blueprint, request
from flask_restful import Api, Resource
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
)
from app import db
from app.models import User
from app.schemas import user_register_schema, user_login_schema, user_schema

# Blueprint for backward compatibility
auth_bp = Blueprint("auth", __name__)
auth_api = Api(auth_bp)


class AuthRegister(Resource):
    """Resource for user registration."""

    def post(self):
        """Register a new user."""
        # Validate input using marshmallow schema
        try:
            data = user_register_schema.load(request.get_json())
        except Exception as err:
            return {"error": err.messages}, 400

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

        return {
            "message": "User registered successfully",
            "user": user_schema.dump(user),
            "access_token": access_token,
            "refresh_token": refresh_token,
        }, 201


class AuthLogin(Resource):
    """Resource for user login."""

    def post(self):
        """Login user and return JWT tokens."""
        # Validate input using marshmallow schema
        try:
            data = user_login_schema.load(request.get_json())
        except Exception as err:
            return {"error": err.messages}, 400

        user = User.query.filter_by(email=data["email"]).first()

        if not user or not user.check_password(data["password"]):
            return {"error": "Invalid email or password"}, 401

        if not user.is_verified:
            return {"error": "Please verify your email first"}, 403

        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)

        return {
            "message": "Login successful",
            "user": user_schema.dump(user),
            "access_token": access_token,
            "refresh_token": refresh_token,
        }, 200


class AuthLogout(Resource):
    """Resource for user logout."""

    @jwt_required()
    def post(self):
        """Logout user (client-side token removal)."""
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        return {
            "message": "Logged out successfully",
            "user": user_schema.dump(user),
        }, 200


class AuthRefresh(Resource):
    """Resource for token refresh."""

    @jwt_required(refresh=True)
    def post(self):
        """Refresh access token."""
        current_user_id = get_jwt_identity()
        access_token = create_access_token(identity=current_user_id)

        return {"access_token": access_token}, 200


class AuthMe(Resource):
    """Resource for getting current user."""

    @jwt_required()
    def get(self):
        """Get current user information."""
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return {"error": "User not found"}, 404

        return {"user": user_schema.dump(user)}, 200


# Register resources with the API
auth_api.add_resource(AuthRegister, "/register")
auth_api.add_resource(AuthLogin, "/login")
auth_api.add_resource(AuthLogout, "/logout")
auth_api.add_resource(AuthRefresh, "/refresh")
auth_api.add_resource(AuthMe, "/me")
