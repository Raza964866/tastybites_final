from flask import Blueprint
from flask_login import LoginManager
from ..backend.models import User, db

# Create admin blueprint
admin_bp = Blueprint('admin', __name__, template_folder='templates', static_folder='static')

# Initialize login manager
login_manager = LoginManager()
login_manager.login_view = 'admin.login'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_admin_module(app):
    """Initialize the admin module with the Flask app"""
    # Initialize login manager
    login_manager.init_app(app)
    
    # Import blueprints
    from . import auth_routes, dashboard_routes, menu_routes, order_routes, user_routes
    
    # Register the main admin blueprint
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # Register other blueprints
    app.register_blueprint(auth_routes.auth_bp)
    app.register_blueprint(dashboard_routes.dashboard_bp)
    app.register_blueprint(menu_routes.menu_bp)
    app.register_blueprint(order_routes.order_bp)
    app.register_blueprint(user_routes.user_bp)
    
    # Register delivery routes
    from ..backend import delivery_routes
    app.register_blueprint(delivery_routes.delivery_bp, url_prefix='/api')
    
    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()
    
    return app
