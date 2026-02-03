"""
Create Admin User Script
Run this to create an admin user for testing
"""

from app import create_app, db
from app.models import User

app = create_app("development")
with app.app_context():
    # Check if admin exists
    admin = User.query.filter_by(email="admin@farmart.com").first()

    if not admin:
        admin = User(
            email="admin@farmart.com",
            first_name="Admin",
            last_name="User",
            phone_number="254700000001",
            role="admin",
            is_verified=True,
        )
        admin.set_password("Admin@123456")
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin user created successfully!")
        print("   Email: admin@farmart.com")
        print("   Password: Admin@123456")
    else:
        # Update role if user exists
        admin.role = "admin"
        admin.is_verified = True
        db.session.commit()
        print("✅ User updated to admin!")
        print("   Email:", admin.email)
        print("   Password: Use existing password")
