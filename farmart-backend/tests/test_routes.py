"""
Integration tests for API routes
"""

import pytest
import json


class TestAuthRoutes:
    """Tests for authentication routes."""

    def test_register_farmer(self, client):
        """Test farmer registration."""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "newfarmer@test.com",
                "password": "NewPassword123",
                "phone_number": "254700000003",
                "first_name": "New",
                "last_name": "Farmer",
                "role": "farmer",
            },
        )

        assert response.status_code == 201
        data = json.loads(response.data)
        assert "user" in data
        assert "access_token" in data

    def test_login_success(self, client, test_farmer):
        """Test successful login."""
        response = client.post(
            "/api/auth/login",
            json={"email": "farmer@test.com", "password": "TestPassword123"},
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert "access_token" in data

    def test_login_wrong_password(self, client, test_farmer):
        """Test login with wrong password."""
        response = client.post(
            "/api/auth/login",
            json={"email": "farmer@test.com", "password": "WrongPassword"},
        )

        assert response.status_code == 401

    def test_get_current_user(self, client, farmer_token):
        """Test get current user endpoint."""
        response = client.get(
            "/api/auth/me", headers={"Authorization": f"Bearer {farmer_token}"}
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert "user" in data


class TestValidation:
    """Tests for input validation."""

    def test_invalid_email(self, client):
        """Test registration with invalid email."""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "invalid-email",
                "password": "NewPassword123",
                "phone_number": "254700000006",
                "first_name": "Test",
                "last_name": "User",
                "role": "buyer",
            },
        )

        assert response.status_code == 400

    def test_weak_password(self, client):
        """Test registration with weak password."""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "test2@example.com",
                "password": "weak",
                "phone_number": "254700000007",
                "first_name": "Test",
                "last_name": "User",
                "role": "buyer",
            },
        )

        assert response.status_code == 400
