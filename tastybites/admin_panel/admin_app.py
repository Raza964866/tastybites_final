from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_required, current_user, login_user, logout_user
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import check_password_hash
from tastybites.backend.models import db, User
from tastybites.admin_panel.admin_routes import admin_bp
from tastybites.backend.config import Config
import os

def create_admin_app():
    app = Flask(__name__,
                template_folder='templates',
                static_folder='static')
    app.config.from_object(Config)
    
    # Set a unique session cookie name for the admin panel
    app.config['SESSION_COOKIE_NAME'] = 'admin_session'

    # Initialize extensions
    db.init_app(app)
    
    # Initialize CSRF protection for admin panel
    csrf = CSRFProtect(app)
    
    # Add CSRF token to template context
    @app.context_processor
    def inject_csrf_token():
        try:
            from flask_wtf.csrf import generate_csrf
            return dict(csrf_token=generate_csrf)
        except Exception:
            return dict(csrf_token=lambda: '')
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'admin_login'
    login_manager.login_message = 'Please log in to access the admin panel.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints
    app.register_blueprint(admin_bp)
    
    # Admin login route
    @app.route('/login', methods=['GET', 'POST'])
    def admin_login():
        if current_user.is_authenticated and current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
            
        if request.method == 'POST':
            try:
                # Validate CSRF token
                from flask_wtf.csrf import validate_csrf, CSRFError
                validate_csrf(request.form.get('csrf_token'))
            except CSRFError:
                flash('CSRF token missing or invalid. Please try again.', 'danger')
                return render_template('admin/login.html')
                
            email = request.form.get('email')
            password = request.form.get('password')
            
            user = User.query.filter_by(email=email).first()
            
            # Check if user exists, password is correct, and user is admin
            if not user or not check_password_hash(user.password, password):
                flash('Invalid email or password.', 'danger')
                return redirect(url_for('admin_login'))
            
            if user.role != 'admin':
                flash('Access denied. Admin privileges required.', 'danger')
                return redirect(url_for('admin_login'))
            
            if not user.is_verified:
                flash('Account not verified. Please contact administrator.', 'warning')
                return redirect(url_for('admin_login'))
            
            login_user(user)
            return redirect(url_for('admin.dashboard'))
        
        return render_template('admin/login.html')
    
    # Admin logout route
    @app.route('/logout')
    @login_required
    def admin_logout():
        logout_user()
        flash('You have been logged out successfully.', 'info')
        return redirect(url_for('admin_login'))
    
    # Admin home route
    @app.route('/')
    def admin_home():
        if current_user.is_authenticated and current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('admin_login'))
    
    return app

if __name__ == '__main__':
    app = create_admin_app()
    print("TastyBites Admin Panel is running at http://127.0.0.1:5001/")
    print("Login with admin credentials to access the admin panel.")
    app.run(debug=True, port=5001, host='127.0.0.1')
