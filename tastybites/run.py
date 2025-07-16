import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tastybites.admin_panel.admin_app import create_admin_app
from tastybites.backend.app import app, db

# Create tables if they don't exist
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    print("TastyBites is running at http://127.0.0.1:5000/")
    app.run(debug=True)
