"""
Unit tests for models
"""

import pytest
from app.models import User, Livestock, UserRole, LivestockStatus


class TestUserModel:
    """Tests for User model."""

    def test_password_hashing(self, app, db_session):
        """Test password hashing and verification."""
        with app.app_context():
            user = User(
                email="test@example.com",
                phone_number="254700000000",
                first_name="Test",
                last_name="User",
                role=UserRole.BUYER,
            )
            user.set_password("TestPassword123")

            assert user.password_hash != "TestPassword123"
            assert user.check_password("TestPassword123")
            assert not user.check_password("WrongPassword")

    def test_user_to_dict(self, app, db_session, test_farmer):
        """Test user to_dict conversion."""
        with app.app_context():
            user = User.query.get(test_farmer.id)
            user_dict = user.to_dict()

            assert "id" in user_dict
            assert "email" in user_dict
            assert "phone_number" in user_dict
            assert "first_name" in user_dict
            assert "last_name" in user_dict
            assert "role" in user_dict
            assert "password_hash" not in user_dict


class TestLivestockModel:
    """Tests for Livestock model."""

    def test_livestock_status_defaults(self, app, db_session, test_farmer):
        """Test livestock status defaults to available."""
        with app.app_context():
            livestock = Livestock(
                farmer_id=test_farmer.id, name="Test Animal", species="goat", price=5000
            )
            db_session.add(livestock)
            db_session.commit()

            assert livestock.status == LivestockStatus.AVAILABLE
