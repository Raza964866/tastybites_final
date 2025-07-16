#!/usr/bin/env python3
"""
Script to fix the admin user verification status
"""

import sys
import os

# Add the project directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tastybites'))

from tastybites.backend.models import db, User
from tastybites.admin_panel.admin_app import create_admin_app

def fix_admin_verification():
    """Fix the admin user verification status"""
    app = create_admin_app()
    
    with app.app_context():
        # Find the admin user
        admin_user = User.query.filter_by(email='admin@tastybites.com').first()
        
        if admin_user:
            # Update verification status
            admin_user.is_verified = True
            
            try:
                db.session.commit()
                print("✓ Admin user verification fixed successfully!")
                print(f"  ID: {admin_user.id}")
                print(f"  Name: {admin_user.name}")
                print(f"  Email: {admin_user.email}")
                print(f"  Role: {admin_user.role}")
                print(f"  Verified: {admin_user.is_verified}")
                print("")
                print("🎉 Admin user is now ready to use!")
            except Exception as e:
                print(f"✗ Error fixing admin user verification: {e}")
                db.session.rollback()
        else:
            print("✗ Admin user not found!")

if __name__ == '__main__':
    print("=== Fixing Admin User Verification ===")
    fix_admin_verification()
    print("Done!")
