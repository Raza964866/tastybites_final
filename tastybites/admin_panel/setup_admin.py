#!/usr/bin/env python3
"""
Script to set up the admin system for TastyBites
This will:
1. Create the admin table in the database
2. Add an admin user with email: syedrazah76@gmail.com and password: raza123
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from werkzeug.security import generate_password_hash
from tastybites.backend.models import db, Admin
from tastybites.backend.app import app

def create_admin_table():
    """Create the admin table if it doesn't exist"""
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            print("✅ Database tables created successfully!")
            
            # Check if admin already exists
            existing_admin = Admin.query.filter_by(email='syedrazah76@gmail.com').first()
            if existing_admin:
                print("⚠️  Admin user already exists!")
                return
            
            # Create admin user
            admin = Admin(
                email='syedrazah76@gmail.com',
                password=generate_password_hash('raza123', method='pbkdf2:sha256')
            )
            
            db.session.add(admin)
            db.session.commit()
            
            print("✅ Admin user created successfully!")
            print("📧 Email: syedrazah76@gmail.com")
            print("🔑 Password: raza123")
            print("\n🎉 Admin setup complete! You can now log in to the admin panel.")
            
        except Exception as e:
            print(f"❌ Error creating admin: {str(e)}")
            db.session.rollback()

if __name__ == '__main__':
    print("🚀 Setting up TastyBites Admin System...")
    print("=" * 50)
    create_admin_table()
    print("=" * 50)
    print("✅ Setup complete!")
