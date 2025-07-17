#!/usr/bin/env python3
"""
Script to run the TastyBites Admin Panel
This script will:
1. Create an admin user if it doesn't exist
2. Start the admin panel on port 5001
"""

import sys
import os

# Add the project directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tastybites'))

from werkzeug.security import generate_password_hash
from tastybites.backend.models import db, User
from tastybites.admin_panel.admin_app import create_admin_app

def create_admin_user_if_not_exists():
    """Create an admin user if it doesn't exist"""
    app = create_admin_app()
    
    with app.app_context():
        # Create database tables if they don't exist
        db.create_all()
        
        # Check if admin user already exists
        admin_user = User.query.filter_by(email='admin@tastybites.com').first()
        
        if not admin_user:
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
            
            try:
                db.session.add(admin_user)
                db.session.commit()
                print("✓ Admin user created successfully!")
                print("  Email: admin@tastybites.com")
                print("  Password: admin123")
                print("  Role: admin")
                print("")
            except Exception as e:
                print(f"✗ Error creating admin user: {e}")
                db.session.rollback()
        else:
            print("✓ Admin user already exists!")
            print(f"  Email: {admin_user.email}")
            print(f"  Role: {admin_user.role}")
            print("")

if __name__ == '__main__':
    print("=== TastyBites Admin Panel ===")
    print("Setting up admin user...")
    
    # Create admin user if needed
    create_admin_user_if_not_exists()
    
    # Create and run the admin app
    app = create_admin_app()
    
    print("Starting TastyBites Admin Panel...")
    print("Admin Panel URL: http://127.0.0.1:5001/")
    print("Login Credentials:")
    print("  Email: admin@tastybites.com")
    print("  Password: admin123")
    print("")
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        app.run(debug=True, port=5001, host='127.0.0.1')
    except KeyboardInterrupt:
        print("\nAdmin panel stopped.")
    except Exception as e:
        print(f"Error running admin panel: {e}")
