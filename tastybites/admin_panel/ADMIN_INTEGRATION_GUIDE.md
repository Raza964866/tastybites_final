# Admin Panel Integration Guide

## Overview
This admin panel provides a complete interface for managing users, menu items, and orders in your TastyBites application.

## Features
- **Dashboard**: Overview of key statistics and metrics
- **User Management**: Add, edit, delete, and manage user accounts
- **Menu Management**: Create, update, and delete menu items with image upload
- **Order Management**: View, update order status, and track orders
- **Authentication**: Admin-only access with role-based permissions
- **Responsive Design**: Mobile-friendly interface
- **Search & Filter**: Easy navigation through large datasets

## Integration Steps

### 1. Update your main Flask app
Add the admin blueprint to your main application:

```python
# In your main app.py or run.py
from tastybites.admin_panel.admin_routes import admin_bp

app.register_blueprint(admin_bp)
```

### 2. Create an admin user
You'll need to create an admin user in your database:

```python
from werkzeug.security import generate_password_hash
from tastybites.backend.models import db, User

# Create admin user
admin_user = User(
    name='Admin User',
    email='admin@tastybites.com',
    phone='1234567890',
    address='Admin Address',
    password=generate_password_hash('admin_password'),
    role='admin',
    is_verified=True
)

db.session.add(admin_user)
db.session.commit()
```

### 3. Update your routes
Make sure your authentication routes handle admin login properly:

```python
# In your auth routes
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # ... existing login logic ...
        
        # After successful login, redirect admin users to admin panel
        if user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('main.index'))
```

### 4. Template Path Configuration
Make sure your Flask app can find the admin templates:

```python
# In your app configuration
app = Flask(__name__, 
            template_folder='templates',
            static_folder='static')

# Or if using blueprints, the admin blueprint already handles this
```

### 5. Static Files
The admin panel uses its own CSS and JavaScript files located in:
- `static/css/admin.css`
- `static/js/admin.js`

### 6. Database Setup
Ensure your database has the following tables:
- `user` (with role field)
- `menu_item`
- `order`
- `order_item`

### 7. Upload Directory
Create the upload directory for menu item images:
```bash
mkdir -p tastybites/frontend/static/images
```

## Usage

### Accessing the Admin Panel
1. Navigate to `/admin` in your browser
2. Login with admin credentials
3. You'll be redirected to the admin dashboard

### Managing Users
- View all users at `/admin/users`
- Add new users at `/admin/users/add`
- Edit existing users by clicking the edit button
- Toggle user status (active/inactive)
- Delete users (if they have no orders)

### Managing Menu Items
- View all menu items at `/admin/menu`
- Add new menu items with image upload
- Edit existing items
- Delete items (if not in any orders)
- Filter by category and search

### Managing Orders
- View all orders at `/admin/orders`
- Update order status in real-time
- Filter by status and search by customer
- View detailed order information

## Security Features
- Role-based access control
- Admin-only route protection
- CSRF protection on forms
- Input validation and sanitization

## Customization
You can customize the admin panel by:
- Modifying the CSS in `static/css/admin.css`
- Adding new routes to `admin_routes.py`
- Creating new templates in `templates/admin/`
- Extending the JavaScript functionality in `static/js/admin.js`

## API Endpoints
The admin panel includes API endpoints for:
- `/admin/api/stats` - Dashboard statistics
- `/admin/api/orders/recent` - Recent orders data

## Troubleshooting
- Ensure all required packages are installed
- Check that the admin user has the correct role
- Verify database connections
- Check file permissions for image uploads
- Ensure templates are in the correct directory structure

## File Structure
```
tastybites/
├── admin_panel/
│   ├── static/
│   │   ├── css/
│   │   │   └── admin.css
│   │   └── js/
│   │       └── admin.js
│   ├── templates/
│   │   └── admin/
│   │       ├── layout.html
│   │       ├── dashboard.html
│   │       ├── manage_users.html
│   │       ├── manage_menu.html
│   │       ├── manage_orders.html
│   │       └── login.html
│   ├── admin_app.py
│   ├── admin_routes.py
│   └── __init__.py
```

## Next Steps
1. Test the admin panel with sample data
2. Customize the styling to match your brand
3. Add additional features as needed
4. Set up proper production deployment
5. Configure backup strategies for admin data
