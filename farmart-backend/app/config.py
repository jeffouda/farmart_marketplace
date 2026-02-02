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


class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "postgresql://postgres:postgres@localhost/farmart_dev"
    )


class ProductionConfig(Config):
    """Production configuration."""

    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)


class TestingConfig(Config):
    """Testing configuration."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "postgresql://postgres:postgres@localhost/farmart_test"
    )
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
