from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from .models import db  # Changed from backend.models to relative import
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from .models import User, MenuItem, Order, OrderItem  # Changed from backend.models
# Change this line
from tastybites.auth_token import generate_reset_token, verify_reset_token

# To this
from ..auth_token import generate_reset_token, verify_reset_token  # For package structure
# OR
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # Add parent directory to path
from auth_token import generate_reset_token, verify_reset_token  # Direct import
from werkzeug.security import generate_password_hash, check_password_hash

from flask_wtf.csrf import CSRFProtect

from datetime import datetime, timedelta
from functools import wraps
import random
import string

# Initialize Flask app
app = Flask(__name__, 
            template_folder='../frontend/templates',
            static_folder='../frontend/static')

app.permanent_session_lifetime = timedelta(minutes=30)

# Configure the database to use MySQL
app.config.from_object('tastybites.backend.config.Config')  # Use full package path

# Set a unique session cookie name for the main website
app.config['SESSION_COOKIE_NAME'] = 'main_session'

# Initialize CSRF protection
csrf = CSRFProtect(app)

# Add CSRF token to template context
@app.context_processor
def inject_csrf_token():
    try:
        from flask_wtf.csrf import generate_csrf
        return dict(csrf_token=generate_csrf)
    except Exception:
        return dict(csrf_token=lambda: '')



# Initialize SQLAlchemy
db.init_app(app)

# Initialize Flask-Mail
# Add this near other imports
from flask_mail import Mail, Message

# Add this after SQLAlchemy initialization
mail = Mail()

# Add these configurations after SQLAlchemy configs

mail.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Import and register blueprints
from .routes import routes_bp  # Changed from backend.routes to relative import
app.register_blueprint(routes_bp)

# Import and register admin panel blueprint
from ..admin_panel.admin_routes import admin_bp
app.register_blueprint(admin_bp)

# Password reset routes
@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        
        if user:
            token = generate_reset_token(user.email)
            reset_url = url_for('reset_with_token', token=token, _external=True)
            
            msg = Message('Password Reset Request', recipients=[user.email])
            msg.body = f'To reset your password, visit: {reset_url}'
            mail.send(msg)
            
            flash('Password reset instructions have been sent to your email.', 'info')
            return redirect(url_for('login'))
        
        flash('Email address not found.', 'danger')
        return redirect(url_for('reset_password'))
    
    return render_template('reset_password.html')

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_with_token(token):
    email = verify_reset_token(token)
    if not email:
        flash('Invalid or expired token.', 'danger')
        return redirect(url_for('reset_password'))

    if request.method == 'POST':
        user = User.query.filter_by(email=email).first()
        if user:
            user.password = generate_password_hash(request.form['password'], method='pbkdf2:sha256')
            db.session.commit()
            flash('Password updated successfully!', 'success')
            return redirect(url_for('login'))
        
        flash('User not found.', 'danger')
        return redirect(url_for('reset_password'))
    
    return render_template('reset_password_confirm.html')







# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/menu')
def menu():
    menu_items = MenuItem.query.all()
    return render_template('menu.html', menu_items=menu_items)

# Custom decorator for admin-only routes
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('You do not have permission to access this page.')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# Helper function to generate verification code
def generate_verification_code():
    return ''.join(random.choices(string.digits, k=6))

# Helper function to send verification email
def send_verification_email(user):
    code = generate_verification_code()
    user.verification_code = code
    db.session.commit()
    
    msg = Message('Verify Your TastyBites Account', recipients=[user.email])
    msg.body = f'''Hello {user.name},

Thank you for signing up with TastyBites! To complete your registration, please verify your email address by entering the following 6-digit code:

{code}

If you did not sign up for TastyBites, please ignore this email.

Best regards,
The TastyBites Team
'''
    mail.send(msg)

# Authentication routes
@app.route('/sign-up', methods=['GET', 'POST'])
def signup():
    error = None
    
    if request.method == 'POST':
        # Get form data
        fullname = request.form.get('fullname')
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address')
        password = request.form.get('password')
        
        # Check if user already exists
        user = User.query.filter_by(email=email).first()
        
        if user:
            error = f"The email address {email} is already registered. Please use a different email or login to your existing account."
            return render_template('signup.html', error=error)
        
        # Create new user
        new_user = User(
            name=fullname,
            email=email,
            phone=phone,
            address=address,
            password=generate_password_hash(password, method='pbkdf2:sha256'),
            role='user',
            is_verified=False
        )
        
        # Add user to database
        db.session.add(new_user)
        db.session.commit()
        
        # Send verification email
        send_verification_email(new_user)
        
        # Store user_id in session for verification
        session['user_id_to_verify'] = new_user.id
        session.permanent = True
        
        # Redirect to verification page
        flash('Please check your email for a verification code.', 'info')
        return redirect(url_for('verify_email'))
    
    return render_template('signup.html', error=error)

# Add these new routes after login route
@app.route('/verify-email', methods=['GET', 'POST'])
def verify_email():
    # Check if there's a user_id in session to verify
    user_id = session.get('user_id_to_verify')
    if not user_id:
        flash('Verification session expired. Please login again.', 'danger')
        return redirect(url_for('login'))
    
    # Get the user from database
    user = User.query.get(user_id)
    if not user:
        flash('User not found. Please register again.', 'danger')
        return redirect(url_for('signup'))
    
    if request.method == 'POST':
        user_code = request.form.get('code')
        
        # Validate the verification code
        if user.verification_code == user_code:
            # Mark user as verified
            user.is_verified = True
            user.verification_code = None  # Clear the code after successful verification
            db.session.commit()
            
            # Remove verification session
            session.pop('user_id_to_verify', None)
            
            flash('Email verified successfully! You can now log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Invalid verification code. Please try again.', 'danger')
    
    return render_template('verify_email.html')

@app.route('/resend-code')
def resend_verification():
    # Check if there's a user_id in session to verify
    user_id = session.get('user_id_to_verify')
    if not user_id:
        flash('Verification session expired. Please login again.', 'danger')
        return redirect(url_for('login'))
    
    # Get the user from database
    user = User.query.get(user_id)
    if not user:
        flash('User not found. Please register again.', 'danger')
        return redirect(url_for('signup'))
    
    # Generate and send new verification code
    send_verification_email(user)
    
    flash('New verification code sent! Please check your email.', 'success')
    return redirect(url_for('verify_email'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if request.is_json:
            return jsonify({'redirect': url_for('index')})
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        # Handle both form and JSON data
        if request.is_json:
            data = request.get_json()
            email = data.get('email')
            password = data.get('password')
            remember = data.get('remember', False)
        else:
            email = request.form.get('email')
            password = request.form.get('password')
            remember = True if request.form.get('remember') else False
        
        user = User.query.filter_by(email=email).first()
        
        # Check if user exists and password is correct
        if not user or not check_password_hash(user.password, password):
            if request.is_json:
                return jsonify({'error': 'Invalid email or password'}), 401
            flash('Please check your login details and try again.', 'danger')
            return redirect(url_for('login'))
        
        # Check if user is verified
        if not user.is_verified:
            # Store user_id in session for verification
            session['user_id_to_verify'] = user.id
            
            # Send verification email
            send_verification_email(user)
            
            if request.is_json:
                return jsonify({
                    'error': 'Please verify your email before logging in.',
                    'redirect': url_for('verify_email')
                }), 403
                
            flash('Please verify your email before logging in.', 'warning')
            return redirect(url_for('verify_email'))
        
        # If validation passes, log in the user
        login_user(user, remember=remember)
        
        # Prepare response data
        response_data = {}
        
        # Redirect admin users to admin panel, regular users to index
        if user.role == 'admin':
            response_data['redirect'] = url_for('admin.dashboard')
        else:
            # Redirect to the page the user was trying to access or home
            next_page = request.args.get('next') or url_for('index')
            response_data['redirect'] = next_page
        
        if request.is_json:
            return jsonify(response_data)
        return redirect(response_data['redirect'])
    
    # If it's a GET request, just render the login page
    if request.is_json:
        return jsonify({'error': 'Method not allowed'}), 405
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# Protected routes
@app.route('/profile')
@login_required
def profile():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.order_date.desc()).all()
    return render_template('profile.html', user=current_user, orders=orders)

@app.route('/order', methods=['GET', 'POST'])
@login_required
def order():
    menu_items = MenuItem.query.all()
    return render_template('order.html', menu_items=menu_items)

# Admin routes
@app.route('/admin')
@login_required
@admin_required
def admin():
    users = User.query.all()
    orders = Order.query.order_by(Order.order_date.desc()).all()
    menu_items = MenuItem.query.all()
    return render_template('admin.html', users=users, orders=orders, menu_items=menu_items)

# Contact form submission
@app.route('/submit-contact', methods=['POST'])
def submit_contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        
        # Here you would typically save this to a database or send an email
        # For now, we'll just flash a message
        flash('Thank you for your message! We will get back to you soon.')
        return redirect(url_for('contact'))

# User authentication status API
@app.route('/api/user/status')
def user_status():
    return jsonify({
        'authenticated': current_user.is_authenticated,
        'user_id': current_user.id if current_user.is_authenticated else None,
        'username': current_user.name if current_user.is_authenticated else None
    })

# Place order route
@app.route('/place-order', methods=['POST'])
def place_order():
    if not current_user.is_authenticated:
        return jsonify({'success': False, 'message': 'Please log in to place an order'}), 401
    
    data = request.get_json()
    items = data.get('items', [])
    
    if not items:
        return jsonify({'success': False, 'message': 'No items in order'}), 400
    
    # Create a new order
    new_order = Order(
        user_id=current_user.id,
        order_date=datetime.now(),
        status='Pending',
        total_amount=data.get('total', 0)
    )
    
    db.session.add(new_order)
    db.session.commit()
    
    # Add order items
    for item in items:
        order_item = OrderItem(
            order_id=new_order.id,
            menu_item_id=item['id'],
            quantity=item['quantity'],
            price=item['price']
        )
        db.session.add(order_item)
    
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Order placed successfully', 'order_id': new_order.id})

# Initialize the database
@app.cli.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    db.create_all()
    print('Initialized the database.')

# REMOVE THESE DUPLICATE ROUTES COMPLETELY
# Delete these lines (around line 270-284)
# @app.route('/profile')
# @login_required
# def profile():
#     orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.order_date.desc()).all()
#     return render_template('profile.html', user=current_user, orders=orders)

# @app.route('/order', methods=['GET', 'POST'])
# @login_required
# def order():
#     menu_items = MenuItem.query.all()
#     return render_template('order.html', menu_items=menu_items)

# Populate with sample data
@app.cli.command('seed-db')
def seed_db_command():
    """Add sample data to the database."""
    # Add sample menu items
    items = [
        MenuItem(name='Classic Burger', description='Juicy beef patty with lettuce, tomato, and special sauce', price=9.99, category='Burgers', image='burger.jpg'),
        MenuItem(name='Margherita Pizza', description='Traditional pizza with tomato sauce, mozzarella, and basil', price=12.99, category='Pizza', image='pizza.jpg'),
        MenuItem(name='Caesar Salad', description='Crisp romaine lettuce with Caesar dressing, croutons, and parmesan', price=7.99, category='Salads', image='salad.jpg'),
        MenuItem(name='Chocolate Brownie', description='Rich chocolate brownie with vanilla ice cream', price=5.99, category='Desserts', image='brownie.jpg')
    ]
    
    for item in items:
        db.session.add(item)
    
    db.session.commit()
    print('Added sample menu items.')

if __name__ == '__main__':
    app.run(debug=True)