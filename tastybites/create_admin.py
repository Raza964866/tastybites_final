import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from werkzeug.security import generate_password_hash
from backend.models import db, User
from backend.app import app

def create_admin_user():
    with app.app_context():
        # Check if admin user already exists
        admin_user = User.query.filter_by(email='admin@tastybites.com').first()
        
        if admin_user:
            print("Admin user already exists!")
            print(f"Email: {admin_user.email}")
            print(f"Role: {admin_user.role}")
            return
        
        # Create admin user
        admin_user = User(
            name='Admin User',
            email='admin@tastybites.com',
            phone='1234567890',
            address='Admin Address',
            password=generate_password_hash('admin123', method='pbkdf2:sha256'),
            role='admin',
            is_verified=True
        )
        
        db.session.add(admin_user)
        db.session.commit()
        
        print("Admin user created successfully!")
        print("Email: admin@tastybites.com")
        print("Password: admin123")
        print("Role: admin")

if __name__ == '__main__':
    create_admin_user()
