# Backend routes
from flask import Blueprint, jsonify, request, session, redirect, url_for, render_template, flash
from flask_login import login_required, current_user
from .models import db
from .models import MenuItem, Order, OrderItem
import json
from datetime import datetime

# Create a Blueprint for the routes
routes_bp = Blueprint('routes', __name__)

# Menu routes
@routes_bp.route('/api/menu')
def get_menu():
    menu_items = MenuItem.query.filter_by(is_available=True).all()
    items = [{
        'id': item.id,
        'name': item.name,
        'description': item.description,
        'price': item.price,
        'category': item.category,
        'image': item.image
    } for item in menu_items]
    return jsonify(items)

# Cart routes
@routes_bp.route('/api/cart/add', methods=['POST'])
def add_to_cart():
    data = request.json
    
    # Initialize cart if it doesn't exist in session
    if 'cart' not in session:
        session['cart'] = []
    
    # Check if item already in cart
    item_id = data.get('id')
    item_exists = False
    
    for item in session['cart']:
        if item['id'] == item_id:
            item['quantity'] += 1
            item_exists = True
            break
    
    # If item not in cart, add it
    if not item_exists:
        session['cart'].append({
            'id': item_id,
            'name': data.get('name'),
            'price': data.get('price'),
            'quantity': 1
        })
    
    # Save session
    session.modified = True
    
    return jsonify({'success': True, 'cart': session['cart']})

@routes_bp.route('/api/cart/update', methods=['POST'])
def update_cart():
    data = request.json
    item_id = data.get('id')
    quantity = data.get('quantity')
    
    if 'cart' in session:
        for item in session['cart']:
            if item['id'] == item_id:
                item['quantity'] = quantity
                if quantity <= 0:
                    session['cart'].remove(item)
                break
        
        session.modified = True
    
    return jsonify({'success': True, 'cart': session.get('cart', [])})

@routes_bp.route('/api/cart/remove', methods=['POST'])
def remove_from_cart():
    data = request.json
    item_id = data.get('id')
    
    if 'cart' in session:
        session['cart'] = [item for item in session['cart'] if item['id'] != item_id]
        session.modified = True
    
    return jsonify({'success': True, 'cart': session.get('cart', [])})

@routes_bp.route('/api/cart/clear', methods=['POST'])
def clear_cart():
    if 'cart' in session:
        session.pop('cart')
    
    return jsonify({'success': True})

@routes_bp.route('/api/cart')
def get_cart():
    return jsonify({'cart': session.get('cart', [])})

@routes_bp.route('/api/cart/save', methods=['POST'])
def save_cart():
    try:
        data = request.get_json()
        if not data or 'cart' not in data:
            return jsonify({'success': False, 'message': 'No cart data provided'}), 400
            
        # Save cart to session
        session['cart'] = data['cart']
        return jsonify({'success': True, 'message': 'Cart saved successfully'})
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error saving cart: {str(e)}'
        }), 500

# Order routes
@routes_bp.route('/api/order/create', methods=['POST'])
@login_required
def create_order():
    try:
        data = request.get_json()
        if not data:
            print("[DEBUG] No data provided in order creation request.")
            return jsonify({'success': False, 'message': 'No data provided'}), 400
            
        items = data.get('items', [])
        if not items:
            print("[DEBUG] No items in order creation request.")
            return jsonify({'success': False, 'message': 'No items in order'}), 400
        
        print(f"[DEBUG] Received order request with {len(items)} items.")
        
        # Calculate total amount and validate items
        total_amount = 0
        order_items = []
        
        for item in items:
            try:
                menu_item = MenuItem.query.get(item['id'])
                if not menu_item:
                    print(f"[DEBUG] Menu item {item['id']} not found.")
                    return jsonify({'success': False, 'message': f'Menu item {item["id"]} not found'}), 404
                    
                quantity = int(item.get('quantity', 1))
                if quantity < 1:
                    print(f"[DEBUG] Invalid quantity for item {item['id']}: {quantity}")
                    return jsonify({'success': False, 'message': 'Invalid quantity'}), 400
                    
                price = float(item.get('price', 0))
                if price <= 0:
                    print(f"[DEBUG] Invalid price for item {item['id']}: {price}")
                    return jsonify({'success': False, 'message': 'Invalid price'}), 400
                    
                total_amount += price * quantity
                
                order_items.append({
                    'menu_item_id': menu_item.id,
                    'quantity': quantity,
                    'price': price,
                    'name': menu_item.name
                })
                print(f"[DEBUG] Validated item: {menu_item.name} (ID: {menu_item.id}, Qty: {quantity}, Price: {price})")
                
            except (KeyError, ValueError) as e:
                print(f"[ERROR] Invalid item data in order request: {str(e)}")
                return jsonify({'success': False, 'message': f'Invalid item data: {str(e)}'}), 400
        
        # Update user information if provided in the form
        user_name = data.get('name')
        user_email = data.get('email')
        user_phone = data.get('phone')
        user_address = data.get('address')
        
        if user_name and user_name.strip():
            current_user.name = user_name.strip()
        if user_email and user_email.strip():
            current_user.email = user_email.strip()
        if user_phone and user_phone.strip():
            current_user.phone = user_phone.strip()
        if user_address and user_address.strip():
            current_user.address = user_address.strip()
        
        # Create new order
        new_order = Order(
            user_id=current_user.id,
            order_date=datetime.utcnow(),
            status='Pending',
            total_amount=total_amount,
            delivery_address=user_address,
            payment_method=data.get('payment_method'),
            notes=data.get('notes')
        )
        
        db.session.add(new_order)
        db.session.flush()  # Get the order ID without committing
        print(f"[DEBUG] New order created with ID: {new_order.id}")
        
        # Create order items
        for item in data['items']:
            order_item = OrderItem(
                order_id=new_order.id,
                menu_item_id=item['id'],
                quantity=item['quantity'],
                price=item['price']
            )
            db.session.add(order_item)
            print(f"[DEBUG] Added order item: {item['name']} (Qty: {item['quantity']})")
        
        # Clear the user's cart after successful order
        if 'cart' in session:
            session.pop('cart')
            print("[DEBUG] User's cart cleared from session.")
        
        # Commit all changes
        db.session.commit()
        print("[DEBUG] Order and order items committed to database.")
        
        return jsonify({
            'success': True, 
            'order_id': new_order.id,
            'message': 'Order placed successfully',
            'redirect': f'/receipt/{new_order.id}'
        })
        
    except Exception as e:
        db.session.rollback()
        import traceback
        print(f"[ERROR] Error creating order: {str(e)}\n{traceback.format_exc()}")
        return jsonify({
            'success': False,
            'message': 'An error occurred while placing your order. Please try again.'
        }), 500

@routes_bp.route('/api/orders')
@login_required
def get_orders():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.order_date.desc()).all()
    
    orders_list = [{
        'id': order.id,
        'date': order.order_date.strftime('%Y-%m-%d %H:%M'),
        'status': order.status,
        'total': order.total_amount
    } for order in orders]
    
    return jsonify(orders_list)

@routes_bp.route('/api/orders/<int:order_id>')
@login_required
def get_order_details(order_id):
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first()
    
    if not order:
        return jsonify({'success': False, 'message': 'Order not found'}), 404
    
    order_items = OrderItem.query.filter_by(order_id=order.id).all()
    
    items = []
    for item in order_items:
        menu_item = MenuItem.query.get(item.menu_item_id)
        items.append({
            'id': item.id,
            'name': menu_item.name,
            'quantity': item.quantity,
            'price': item.price,
            'total': item.price * item.quantity
        })
    
    order_details = {
        'id': order.id,
        'date': order.order_date.strftime('%Y-%m-%d %H:%M'),
        'status': order.status,
        'total': order.total_amount,
        'items': items
    }
    
    return jsonify(order_details)

# Authentication check
@routes_bp.route('/api/check-auth')
def check_auth():
    return jsonify({
        'authenticated': current_user.is_authenticated
    })

# Page routes
@routes_bp.route('/menu')
def menu_page():
    # Optional: Check if user has provided location (commented out to avoid redirect loop)
    # user_location = session.get('user_location')
    # if not user_location:
    #     return redirect(url_for('routes.location_page'))
    
    menu_items = MenuItem.query.filter_by(is_available=True).all()
    return render_template('menu.html', menu_items=menu_items)

@routes_bp.route('/location', methods=['GET', 'POST'])
def location_page():
    if request.method == 'POST':
        try:
            # Log request details for debugging
            print(f"[DEBUG] Content-Type: {request.content_type}")
            print(f"[DEBUG] Request headers: {dict(request.headers)}")
            print(f"[DEBUG] Raw request data: {request.data}")
            
            data = request.get_json(force=True)
            print(f"[DEBUG] Location request data: {data}")
            print(f"[DEBUG] Data type: {type(data)}")
            
            if data and isinstance(data, dict):
                latitude = data.get('latitude')
                longitude = data.get('longitude')
                
                print(f"[DEBUG] Latitude: {latitude}, Longitude: {longitude}")
                
                if latitude is not None and longitude is not None:
                    # Store location in session
                    session['user_location'] = {
                        'latitude': float(latitude),
                        'longitude': float(longitude),
                        'address': data.get('address', ''),
                        'skipped': data.get('skipped', False)
                    }
                    session.permanent = True
                    print(f"[DEBUG] Location saved to session: {session['user_location']}")
                    
                    # Different message based on whether location was skipped
                    if data.get('skipped', False):
                        print("[DEBUG] Location skipped successfully")
                        return jsonify({'success': True, 'message': 'Location skipped successfully'})
                    else:
                        print("[DEBUG] Location saved successfully")
                        return jsonify({'success': True, 'message': 'Location saved successfully'})
                else:
                    print(f"[DEBUG] Missing latitude or longitude. Data: {data}")
                    return jsonify({'success': False, 'message': 'Missing latitude or longitude'}), 400
            else:
                print(f"[DEBUG] Invalid data format. Data: {data}, Type: {type(data)}")
                return jsonify({'success': False, 'message': 'Invalid data format'}), 400
        except Exception as e:
            print(f"[ERROR] Error in location route: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500
    
    return render_template('location.html')

@routes_bp.route('/test-location')
def test_location_page():
    """Test page for debugging location functionality"""
    return render_template('test_location.html')

@routes_bp.route('/checkout')
@login_required
def checkout_page():
    cart = session.get('cart', [])
    
    if not cart:
        flash('Your cart is empty', 'warning')
        return redirect(url_for('menu_page'))
    
    total = sum(item['price'] * item['quantity'] for item in cart)
    
    return render_template('checkout.html', cart=cart, total=total)

@routes_bp.route('/receipt/<int:order_id>')
@login_required
def receipt_page(order_id):
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first()
    
    if not order:
        flash('Order not found', 'danger')
        return redirect(url_for('profile'))
    
    order_items = OrderItem.query.filter_by(order_id=order.id).all()
    
    items = []
    for item in order_items:
        menu_item = MenuItem.query.get(item.menu_item_id)
        items.append({
            'name': menu_item.name,
            'quantity': item.quantity,
            'price': item.price,
            'total': item.price * item.quantity
        })
    
    return render_template('receipt.html', order=order, items=items)