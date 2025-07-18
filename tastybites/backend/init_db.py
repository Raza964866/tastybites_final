from flask import Flask
from flask_mysqldb import MySQL
import os

# Create a Flask app instance
app = Flask(__name__)

# Initialize MySQL
mysql = MySQL()

def init_mysql(app):
    app.config['MYSQL_HOST'] = 'localhost'
    
    return mysql

def init_db():
    # Initialize MySQL with our Flask app
    init_mysql(app)
    
    try:
        # Connect to MySQL and create cursor
        conn = mysql.connection
        if conn is None:
            print("Error: Could not connect to MySQL database.")
            print("Please check if MySQL server is running and credentials are correct.")
            return
            
        cursor = conn.cursor()
        
        # Read SQL script
        with open(os.path.join(os.path.dirname(__file__), 'init_db.sql'), 'r') as f:
            sql_script = f.read()
        
        # Execute each statement in the script
        for statement in sql_script.split(';'):
            if statement.strip():
                cursor.execute(statement)
        
        # Add email verification columns to user table
        try:
            cursor.execute('ALTER TABLE user ADD COLUMN is_verified BOOLEAN DEFAULT FALSE')
            cursor.execute('ALTER TABLE user ADD COLUMN verification_code VARCHAR(6)')
            print("Added email verification columns to user table")
        except Exception as e:
            # If columns already exist, this will catch the error
            print(f"Note: {e}")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("Database initialized successfully!")
    except Exception as e:
        print(f"Database initialization failed: {e}")

if __name__ == "__main__":
    init_db()
