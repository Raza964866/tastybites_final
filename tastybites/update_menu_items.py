#!/usr/bin/env python3
"""
Database migration script to add new fields to MenuItem table
Run this script to update existing menu items with the new fields.
"""

import sys
import os

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tastybites.backend.app import app, db
from tastybites.backend.models import MenuItem
from datetime import datetime

def migrate_menu_items():
    with app.app_context():
        try:
            # Check if the new columns exist
            from sqlalchemy import text
            
            # Check if is_available column exists
            result = db.session.execute(text("DESCRIBE menu_item")).fetchall()
            columns = [column[0] for column in result]
            
            if 'is_available' not in columns:
                # Add the is_available column with default value True
                db.session.execute(text("ALTER TABLE menu_item ADD COLUMN is_available BOOLEAN DEFAULT 1 NOT NULL"))
                print("Added is_available column to menu_item table")
            
            if 'created_at' not in columns:
                # Add the created_at column with default value current timestamp
                db.session.execute(text("ALTER TABLE menu_item ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP"))
                print("Added created_at column to menu_item table")
            
            db.session.commit()
            print("Migration completed successfully!")
            
        except Exception as e:
            print(f"Error during migration: {e}")
            db.session.rollback()

if __name__ == "__main__":
    migrate_menu_items()
