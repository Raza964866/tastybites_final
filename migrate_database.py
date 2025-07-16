#!/usr/bin/env python3
"""
Database migration script to add new columns to the Order table
"""

import sys
import os
from urllib.parse import unquote
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tastybites.backend.config import Config
import MySQLdb

def migrate_database():
    """Add new columns to the Order table"""
    
    # Parse database connection details from URI
    try:
        db_uri = Config.SQLALCHEMY_DATABASE_URI.replace("mysql://", "")
        user_pass, host_db = db_uri.split("@")
        user, password = user_pass.split(":")
        password = unquote(password)  # URL decode the password
        host, database = host_db.split("/")
        
        connection = MySQLdb.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            charset='utf8mb4'
        )
        
        cursor = connection.cursor()
        
        print("Starting database migration...")
        
        # Check if columns already exist
        cursor.execute("SHOW COLUMNS FROM `order` LIKE 'latitude'")
        if cursor.fetchone():
            print("Columns already exist. Migration not needed.")
            return
        
        # Add new columns to the order table
        migration_queries = [
            "ALTER TABLE `order` ADD COLUMN `latitude` FLOAT NULL AFTER `total_amount`",
            "ALTER TABLE `order` ADD COLUMN `longitude` FLOAT NULL AFTER `latitude`",
            "ALTER TABLE `order` ADD COLUMN `delivery_address` TEXT NULL AFTER `longitude`",
            "ALTER TABLE `order` ADD COLUMN `notes` TEXT NULL AFTER `delivery_address`",
            "ALTER TABLE `order` ADD COLUMN `payment_method` VARCHAR(50) NULL AFTER `notes`",
            "ALTER TABLE `order` ADD COLUMN `payment_status` VARCHAR(20) DEFAULT 'Pending' AFTER `payment_method`",
            "ALTER TABLE `order` ADD COLUMN `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP AFTER `payment_status`"
        ]
        
        for query in migration_queries:
            try:
                print(f"Executing: {query}")
                cursor.execute(query)
                print("✓ Success")
            except MySQLdb.OperationalError as e:
                if "Duplicate column name" in str(e):
                    print(f"✓ Column already exists, skipping")
                else:
                    print(f"✗ Error: {e}")
                    raise e
        
        # Commit changes
        connection.commit()
        print("\n✅ Database migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        if 'connection' in locals():
            connection.rollback()
        raise e
    
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

if __name__ == "__main__":
    migrate_database()
