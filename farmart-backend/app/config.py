"""
Configuration for FarmAT Backend
Environment-based configuration management
"""

import os
from datetime import timedelta


class Config:
    """Base configuration class."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "jwt-dev-secret-key")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)

    # JWT Configuration for cookie-based authentication (Secure Handshake)
    # Use both cookies AND headers for redundancy during file uploads
    JWT_TOKEN_LOCATION = ["cookies", "headers"]
    JWT_ACCESS_TOKEN_HEADER_NAME = "Authorization"
    JWT_ACCESS_TOKEN_QUERY_STRING_ARG = "token"
    JWT_COOKIE_SECURE = True  # Set to True in production with HTTPS
    JWT_COOKIE_HTTPONLY = True  # Prevents XSS from accessing tokens
    JWT_COOKIE_SAMESITE = "Lax"  # CSRF protection
    JWT_COOKIE_CSRF_PROTECT = False  # Disable for local development

    # Database
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }

    # M-Pesa Configuration
    MPESA_CONSUMER_KEY = os.environ.get("MPESA_CONSUMER_KEY")
    MPESA_CONSUMER_SECRET = os.environ.get("MPESA_CONSUMER_SECRET")
    MPESA_PASSKEY = os.environ.get("MPESA_PASSKEY")
    MPESA_BUSINESS_SHORT_CODE = os.environ.get("MPESA_BUSINESS_SHORT_CODE", "174379")
    MPESA_CALLBACK_URL = os.environ.get("MPESA_CALLBACK_URL")
    MPESA_ENVIRONMENT = os.environ.get("MPESA_ENVIRONMENT", "sandbox")

    # File Upload
    UPLOAD_FOLDER = "uploads"
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "csv", "xlsx"}

    # Cloudinary Configuration
    CLOUDINARY_CLOUD_NAME = os.environ.get("CLOUDINARY_CLOUD_NAME")
    CLOUDINARY_API_KEY = os.environ.get("CLOUDINARY_API_KEY")
    CLOUDINARY_API_SECRET = os.environ.get("CLOUDINARY_API_SECRET")

    # Frontend URL for CORS
    FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:5173")


class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///farmart_dev.db")

    # Allow non-secure cookies for localhost development
    JWT_COOKIE_SECURE = False


class ProductionConfig(Config):
    """Production configuration."""

    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")

    # Production requires secure cookies (HTTPS only)
    JWT_COOKIE_SECURE = True

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)


class TestingConfig(Config):
    """Testing configuration."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///farmart_test.db"
    )
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}


def config_by_name(config_name: str):
    """Get configuration class by name."""
    config_map = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
        "testing": TestingConfig,
        "default": DevelopmentConfig,
    }
    return config_map.get(config_name, DevelopmentConfig)
