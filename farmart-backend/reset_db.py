"""
Reset Database Script
Drops all tables and recreates them to ensure schema is fresh.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User, Livestock, Order  # Import all models to ensure they are registered

def reset_database():
    app = create_app()
    with app.app_context():
        print("Dropping all tables...")
        db.drop_all()
        print("Creating all tables...")
        db.create_all()
        print("Database schema reset successfully!")

if __name__ == "__main__":
    reset_database()
