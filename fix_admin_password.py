#!/usr/bin/env python3
"""
Script to fix the admin user password hash
This will update the existing admin user's password with proper hash method
"""

import sys
import os

# Add the project directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tastybites'))

from werkzeug.security import generate_password_hash
from tastybites.backend.models import db, User
from tastybites.admin_panel.admin_app import create_admin_app

def fix_admin_password():
    """Fix the admin user password hash"""
    app = create_admin_app()
    
    with app.app_context():
        # Find the admin user
        admin_user = User.query.filter_by(email='admin@tastybites.com').first()
        
        if admin_user:
            # Update the password with proper hash method
            admin_user.password = generate_password_hash('admin123', method='pbkdf2:sha256')
            
            try:
                db.session.commit()
                print("✓ Admin user password fixed successfully!")
                print("  Email: admin@tastybites.com")
                print("  Password: admin123")
                print("  Hash method: pbkdf2:sha256")
            except Exception as e:
                print(f"✗ Error fixing admin user password: {e}")
                db.session.rollback()
        else:
            print("✗ Admin user not found!")

if __name__ == '__main__':
    print("=== Fixing Admin User Password ===")
    fix_admin_password()
    print("Done!")
