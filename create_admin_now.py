#!/usr/bin/env python3
"""
Create admin user with correct credentials
"""

import sys
import os
sys.path.append('tastybites')

from werkzeug.security import generate_password_hash
from tastybites.backend.models import db, User
from tastybites.admin_panel.admin_app import create_admin_app

def create_admin_user():
    """Create admin user with correct credentials"""
    app = create_admin_app()
    
    with app.app_context():
        # Create database tables if they don't exist
        db.create_all()
        
        # Check if admin user already exists
        admin_user = User.query.filter_by(email='syedrazah76@gmail.com').first()
        
        if admin_user:
            print(f"Admin user already exists: {admin_user.email}")
            print(f"Role: {admin_user.role}")
            print(f"Verified: {admin_user.is_verified}")
            if admin_user.role != 'admin':
                print("Updating user role to admin...")
                admin_user.role = 'admin'
                admin_user.is_verified = True
                db.session.commit()
                print("User role updated to admin!")
        else:
            # Create admin user
            admin_user = User(
                name='Admin User',
                email='syedrazah76@gmail.com',
                phone='1234567890',
                address='Admin Address',
                password=generate_password_hash('raza123', method='pbkdf2:sha256'),
                role='admin',
                is_verified=True
            )
            
            try:
                db.session.add(admin_user)
                db.session.commit()
                print("✓ Admin user created successfully!")
                print("  Email: syedrazah76@gmail.com")
                print("  Password: raza123")
                print("  Role: admin")
            except Exception as e:
                print(f"✗ Error creating admin user: {e}")
                db.session.rollback()

if __name__ == '__main__':
    create_admin_user()
