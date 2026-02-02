"""
Pytest configuration and fixtures
"""

import pytest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User


@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app("testing")
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def db_session(app):
    """Create database session."""
    return db.session


@pytest.fixture
def test_farmer(db_session):
    """Create a test farmer user."""
    user = User(
        email="farmer@test.com",
        phone_number="254700000001",
        first_name="Test",
        last_name="Farmer",
        role="farmer",
    )
    user.set_password("TestPassword123")
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def test_buyer(db_session):
    """Create a test buyer user."""
    user = User(
        email="buyer@test.com",
        phone_number="254700000002",
        first_name="Test",
        last_name="Buyer",
        role="buyer",
    )
    user.set_password("TestPassword123")
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def farmer_token(client, test_farmer):
    """Get farmer JWT token."""
    response = client.post(
        "/api/auth/login",
        json={"email": "farmer@test.com", "password": "TestPassword123"},
    )
    return response.json.get("access_token")


@pytest.fixture
def buyer_token(client, test_buyer):
    """Get buyer JWT token."""
    response = client.post(
        "/api/auth/login",
        json={"email": "buyer@test.com", "password": "TestPassword123"},
    )
    return response.json.get("access_token")
