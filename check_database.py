#!/usr/bin/env python3
"""
Script to check the database structure and admin user
"""

import sys
import os

# Add the project directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tastybites'))

from tastybites.backend.models import db, User
from tastybites.admin_panel.admin_app import create_admin_app

def check_database():
    """Check database structure and admin user"""
    app = create_admin_app()
    
    with app.app_context():
        try:
            # Check if tables exist
            print("=== Checking Database Structure ===")
            
            # Create all tables if they don't exist
            db.create_all()
            print("✓ Database tables created/verified")
            
            # Check User table structure
            print("\n=== User Table Structure ===")
            users = User.query.all()
            print(f"Total users in database: {len(users)}")
            
            # Check for admin users
            admin_users = User.query.filter_by(role='admin').all()
            print(f"Admin users found: {len(admin_users)}")
            
            if admin_users:
                print("\n--- Admin Users ---")
                for admin in admin_users:
                    print(f"  ID: {admin.id}")
                    print(f"  Name: {admin.name}")
                    print(f"  Email: {admin.email}")
                    print(f"  Role: {admin.role}")
                    print(f"  Verified: {admin.is_verified}")
                    print(f"  Password Hash: {admin.password[:20]}...")
                    print("---")
            else:
                print("✗ No admin users found!")
                
            # Check regular users
            regular_users = User.query.filter_by(role='user').all()
            print(f"\nRegular users found: {len(regular_users)}")
            
            if regular_users:
                print("\n--- Regular Users ---")
                for user in regular_users[:5]:  # Show first 5 users
                    print(f"  ID: {user.id}, Name: {user.name}, Email: {user.email}")
                if len(regular_users) > 5:
                    print(f"  ... and {len(regular_users) - 5} more")
            
        except Exception as e:
            print(f"✗ Error checking database: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    check_database()
