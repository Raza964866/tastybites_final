from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_required, current_user
from flask_wtf.csrf import validate_csrf, CSRFError
from werkzeug.security import generate_password_hash, check_password_hash
from tastybites.backend.models import db, User, MenuItem, Order, OrderItem
from tastybites.backend.config import Config
from datetime import datetime
import os
from werkzeug.utils import secure_filename

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Upload folder configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'frontend', 'static', 'images')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Ensure upload directory exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def admin_required(f):
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Access denied. Admin privileges required.', 'danger')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    # Get statistics
    total_users = User.query.filter_by(role='user').count()
    total_menu_items = MenuItem.query.count()
    total_orders = Order.query.count()
    pending_orders = Order.query.filter_by(status='Pending').count()
    completed_orders = Order.query.filter_by(status='Completed').count()
    
    # Get recent orders
    recent_orders = Order.query.order_by(Order.order_date.desc()).limit(5).all()
    
    # Calculate total revenue
    total_revenue = db.session.query(db.func.sum(Order.total_amount)).scalar() or 0
    
    stats = {
        'total_users': total_users,
        'total_menu_items': total_menu_items,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'completed_orders': completed_orders,
        'total_revenue': total_revenue,
        'recent_orders': recent_orders
    }
    
    return render_template('admin/dashboard.html', stats=stats)

# User Management Routes
@admin_bp.route('/users')
@login_required
@admin_required
def manage_users():
    search = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    users_query = User.query.filter_by(role='user')
    
    if search:
        users_query = users_query.filter(
            (User.name.contains(search)) | 
            (User.email.contains(search)) | 
            (User.phone.contains(search))
        )
    
    users = users_query.paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('admin/manage_users.html', users=users, search=search)

@admin_bp.route('/users/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_user():
    if request.method == 'POST':
        try:
            # Validate CSRF token
            validate_csrf(request.form.get('csrf_token'))
        except CSRFError:
            flash('CSRF token missing or invalid. Please try again.', 'danger')
            return render_template('admin/add_user.html')
            
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address')
        password = request.form.get('password')
        role = request.form.get('role', 'user')
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            flash('User with this email already exists!', 'danger')
            return render_template('admin/add_user.html')
        
        # Create new user
        new_user = User(
            name=name,
            email=email,
            phone=phone,
            address=address,
            password=generate_password_hash(password, method='pbkdf2:sha256'),
            role=role,
            is_verified=True
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('User added successfully!', 'success')
        return redirect(url_for('admin.manage_users'))
    
    return render_template('admin/add_user.html')

@admin_bp.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        try:
            # Validate CSRF token
            validate_csrf(request.form.get('csrf_token'))
        except CSRFError:
            flash('CSRF token missing or invalid. Please try again.', 'danger')
            return render_template('admin/edit_user.html', user=user)
            
        user.name = request.form.get('name')
        user.email = request.form.get('email')
        user.phone = request.form.get('phone')
        user.address = request.form.get('address')
        user.role = request.form.get('role', 'user')
        
        password = request.form.get('password')
        if password:
            user.password = generate_password_hash(password, method='pbkdf2:sha256')
        
        db.session.commit()
        flash('User updated successfully!', 'success')
        return redirect(url_for('admin.manage_users'))
    
    return render_template('admin/edit_user.html', user=user)

@admin_bp.route('/users/delete/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    try:
        # Validate CSRF token
        validate_csrf(request.form.get('csrf_token'))
    except CSRFError:
        flash('CSRF token missing or invalid. Please try again.', 'danger')
        return redirect(url_for('admin.manage_users'))
        
    user = User.query.get_or_404(user_id)
    
    # Check if user has orders
    if user.orders:
        flash('Cannot delete user with existing orders!', 'danger')
    else:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully!', 'success')
    
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/users/toggle-status/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def toggle_user_status(user_id):
    try:
        # Validate CSRF token
        validate_csrf(request.form.get('csrf_token'))
    except CSRFError:
        flash('CSRF token missing or invalid. Please try again.', 'danger')
        return redirect(url_for('admin.manage_users'))
        
    user = User.query.get_or_404(user_id)
    user.is_verified = not user.is_verified
    db.session.commit()
    
    status = 'activated' if user.is_verified else 'deactivated'
    flash(f'User {status} successfully!', 'success')
    return redirect(url_for('admin.manage_users'))

# Menu Management Routes
@admin_bp.route('/menu')
@login_required
@admin_required
def manage_menu():
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    menu_query = MenuItem.query
    
    if search:
        menu_query = menu_query.filter(
            (MenuItem.name.contains(search)) | 
            (MenuItem.description.contains(search))
        )
    
    if category:
        menu_query = menu_query.filter(MenuItem.category == category)
    
    menu_items = menu_query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Get all categories for filter
    categories = db.session.query(MenuItem.category).distinct().all()
    categories = [cat[0] for cat in categories]
    
    return render_template('admin/manage_menu.html', menu_items=menu_items, 
                         categories=categories, search=search, selected_category=category)

@admin_bp.route('/menu/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_menu_item():
    if request.method == 'POST':
        try:
            # Validate CSRF token
            validate_csrf(request.form.get('csrf_token'))
        except CSRFError:
            flash('CSRF token missing or invalid. Please try again.', 'danger')
            return render_template('admin/add_menu_item.html')
            
        name = request.form.get('name')
        description = request.form.get('description')
        price = float(request.form.get('price'))
        category = request.form.get('category')
        
        # Handle image upload
        image_filename = 'default.jpg'
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Add timestamp to avoid conflicts
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                image_filename = timestamp + filename
                file.save(os.path.join(UPLOAD_FOLDER, image_filename))
        
        new_item = MenuItem(
            name=name,
            description=description,
            price=price,
            category=category,
            image=image_filename,
            is_available=bool(request.form.get('is_available', True))
        )
        
        db.session.add(new_item)
        db.session.commit()
        
        flash('Menu item added successfully!', 'success')
        return redirect(url_for('admin.manage_menu'))
    
    return render_template('admin/add_menu_item.html')

@admin_bp.route('/menu/edit/<int:item_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_menu_item(item_id):
    item = MenuItem.query.get_or_404(item_id)
    
    if request.method == 'POST':
        try:
            # Validate CSRF token
            validate_csrf(request.form.get('csrf_token'))
        except CSRFError:
            flash('CSRF token missing or invalid. Please try again.', 'danger')
            return render_template('admin/edit_menu_item.html', item=item)
            
        item.name = request.form.get('name')
        item.description = request.form.get('description')
        item.price = float(request.form.get('price'))
        item.category = request.form.get('category')
        item.is_available = bool(request.form.get('is_available'))
        
        # Handle image upload
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                image_filename = timestamp + filename
                file.save(os.path.join(UPLOAD_FOLDER, image_filename))
                
                # Delete old image if it's not default
                if item.image != 'default.jpg':
                    old_image_path = os.path.join(UPLOAD_FOLDER, item.image)
                    if os.path.exists(old_image_path):
                        os.remove(old_image_path)
                
                item.image = image_filename
        
        db.session.commit()
        flash('Menu item updated successfully!', 'success')
        return redirect(url_for('admin.manage_menu'))
    
    return render_template('admin/edit_menu_item.html', item=item)

@admin_bp.route('/menu/delete/<int:item_id>', methods=['POST'])
@login_required
@admin_required
def delete_menu_item(item_id):
    try:
        # Validate CSRF token
        validate_csrf(request.form.get('csrf_token'))
    except CSRFError:
        flash('CSRF token missing or invalid. Please try again.', 'danger')
        return redirect(url_for('admin.manage_menu'))
        
    item = MenuItem.query.get_or_404(item_id)
    
    # Check if item is in any orders
    if item.order_items:
        flash('Cannot delete menu item that has been ordered!', 'danger')
    else:
        # Delete image file if it's not default
        if item.image != 'default.jpg':
            image_path = os.path.join(UPLOAD_FOLDER, item.image)
            if os.path.exists(image_path):
                os.remove(image_path)
        
        db.session.delete(item)
        db.session.commit()
        flash('Menu item deleted successfully!', 'success')
    
    return redirect(url_for('admin.manage_menu'))

@admin_bp.route('/menu/toggle-availability/<int:item_id>', methods=['POST'])
@login_required
@admin_required
def toggle_menu_item_availability(item_id):
    try:
        # Validate CSRF token
        validate_csrf(request.form.get('csrf_token'))
    except CSRFError:
        flash('CSRF token missing or invalid. Please try again.', 'danger')
        return redirect(url_for('admin.manage_menu'))
        
    item = MenuItem.query.get_or_404(item_id)
    item.is_available = not item.is_available
    db.session.commit()
    
    status = 'available' if item.is_available else 'unavailable'
    flash(f'Menu item marked as {status}!', 'success')
    return redirect(url_for('admin.manage_menu'))

# Order Management Routes
@admin_bp.route('/orders')
@login_required
@admin_required
def manage_orders():
    status_filter = request.args.get('status', '')
    search = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    orders_query = Order.query
    
    if status_filter:
        orders_query = orders_query.filter(Order.status == status_filter)
    
    if search:
        orders_query = orders_query.join(User).filter(
            (User.name.contains(search)) | 
            (User.email.contains(search)) |
            (Order.id.like(f'%{search}%'))
        )
    
    orders = orders_query.order_by(Order.order_date.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('admin/manage_orders.html', orders=orders, 
                         search=search, status_filter=status_filter)

@admin_bp.route('/orders/view/<int:order_id>')
@login_required
@admin_required
def view_order(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('admin/view_order.html', order=order, config=Config)

@admin_bp.route('/orders/update-status/<int:order_id>', methods=['POST'])
@login_required
@admin_required
def update_order_status(order_id):
    try:
        # Validate CSRF token
        validate_csrf(request.form.get('csrf_token'))
    except CSRFError:
        flash('CSRF token missing or invalid. Please try again.', 'danger')
        return redirect(url_for('admin.manage_orders'))
        
    try:
        order = Order.query.get_or_404(order_id)
        new_status = request.form.get('status')
        
        if new_status in ['Pending', 'Confirmed', 'Preparing', 'Ready', 'Delivered', 'Cancelled']:
            order.status = new_status
            db.session.commit()
            
            # Check if it's an AJAX request
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True, 'message': f'Order status updated to {new_status}!'})
            else:
                flash(f'Order status updated to {new_status}!', 'success')
                return redirect(url_for('admin.view_order', order_id=order_id))
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': 'Invalid status!'}), 400
            else:
                flash('Invalid status!', 'danger')
                return redirect(url_for('admin.view_order', order_id=order_id))
    except Exception as e:
        db.session.rollback()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'Error updating order status'}), 500
        else:
            flash('Error updating order status', 'danger')
            return redirect(url_for('admin.view_order', order_id=order_id))

# API Routes for AJAX requests
@admin_bp.route('/api/stats')
@login_required
@admin_required
def api_stats():
    stats = {
        'total_users': User.query.filter_by(role='user').count(),
        'total_menu_items': MenuItem.query.count(),
        'total_orders': Order.query.count(),
        'pending_orders': Order.query.filter_by(status='Pending').count(),
        'total_revenue': db.session.query(db.func.sum(Order.total_amount)).scalar() or 0
    }
    return jsonify(stats)

@admin_bp.route('/api/orders/recent')
@login_required
@admin_required
def api_recent_orders():
    orders = Order.query.order_by(Order.order_date.desc()).limit(5).all()
    orders_data = []
    
    for order in orders:
        orders_data.append({
            'id': order.id,
            'user_name': order.user.name,
            'total_amount': order.total_amount,
            'status': order.status,
            'order_date': order.order_date.strftime('%Y-%m-%d %H:%M')
        })
    
    return jsonify(orders_data)

