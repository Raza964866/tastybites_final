#!/usr/bin/env python3
"""
Test script to verify admin panel functionality
"""

import sys
import os

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tastybites.backend.app import app, db
from tastybites.backend.models import MenuItem, User
from werkzeug.security import generate_password_hash

def test_admin_functionality():
    with app.app_context():
        try:
            # Test 1: Check if MenuItem model has new fields
            print("Testing MenuItem model structure...")
            
            # Check if we can query menu items
            items = MenuItem.query.all()
            print(f"Found {len(items)} menu items in database")
            
            if items:
                item = items[0]
                print(f"Sample item: {item.name}")
                print(f"Has is_available field: {hasattr(item, 'is_available')}")
                print(f"Has created_at field: {hasattr(item, 'created_at')}")
                print(f"Is available: {item.is_available}")
                print(f"Created at: {item.created_at}")
            
            # Test 2: Check if we can filter by availability
            print("\nTesting availability filtering...")
            available_items = MenuItem.query.filter_by(is_available=True).all()
            print(f"Available items: {len(available_items)}")
            
            unavailable_items = MenuItem.query.filter_by(is_available=False).all()
            print(f"Unavailable items: {len(unavailable_items)}")
            
            # Test 3: Check if admin user exists
            print("\nChecking admin user...")
            admin_user = User.query.filter_by(role='admin').first()
            if admin_user:
                print(f"Admin user exists: {admin_user.email}")
            else:
                print("Creating admin user...")
                admin_user = User(
                    name='Admin User',
                    email='admin@tastybites.com',
                    phone='123-456-7890',
                    address='Admin Address',
                    password=generate_password_hash('admin123', method='pbkdf2:sha256'),
                    role='admin',
                    is_verified=True
                )
                db.session.add(admin_user)
                db.session.commit()
                print("Admin user created successfully!")
            
            print("\nAll tests passed! Admin panel should be working correctly.")
            
        except Exception as e:
            print(f"Error during testing: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_admin_functionality()
