#!/usr/bin/env python3
"""
Simple script to create an admin user for TastyBites Admin Panel
Run this script to create an admin user in the database
"""

import sys
import os

# Add the project directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tastybites'))

from werkzeug.security import generate_password_hash
from tastybites.backend.models import db, User
from tastybites.backend.app import app

def create_admin_user():
    """Create an admin user with credentials"""
    
    print("Creating admin user for TastyBites Admin Panel...")
    
    with app.app_context():
        # Create database tables if they don't exist
        db.create_all()
        
        # Check if admin user already exists
        admin_user = User.query.filter_by(email='admin@tastybites.com').first()
        
        if admin_user:
            print(f"✓ Admin user already exists!")
            print(f"  Email: {admin_user.email}")
            print(f"  Role: {admin_user.role}")
            print(f"  Status: {'Active' if admin_user.is_verified else 'Inactive'}")
            return
        
        # Create admin user
        admin_user = User(
            name='Admin User',
            email='admin@tastybites.com',
            phone='1234567890',
            address='Admin Address',
            password=generate_password_hash('admin123'),
            role='admin',
            is_verified=True
        )
        
        try:
            db.session.add(admin_user)
            db.session.commit()
            
            print("✓ Admin user created successfully!")
            print("  Email: admin@tastybites.com")
            print("  Password: admin123")
            print("  Role: admin")
            print("")
            print("You can now access the admin panel at:")
            print("  http://127.0.0.1:5000/admin")
            print("")
            print("Login with the credentials above to manage users, menu items, and orders.")
            
        except Exception as e:
            print(f"✗ Error creating admin user: {e}")
            db.session.rollback()

if __name__ == '__main__':
    create_admin_user()
