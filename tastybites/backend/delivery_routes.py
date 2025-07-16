from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from . import db
from .models import Order
from functools import wraps

delivery_bp = Blueprint('delivery', __name__)

def delivery_person_required(f):
    """Decorator to ensure the user is a delivery person"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'delivery':
            return jsonify({'success': False, 'message': 'Delivery person access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

@delivery_bp.route('/api/delivery/orders/available', methods=['GET'])
@login_required
@delivery_person_required
def get_available_orders():
    """Get all available orders for delivery"""
    available_orders = Order.query.filter(
        Order.status == 'Confirmed',
        Order.delivery_person_id.is_(None)
    ).all()
    
    return jsonify({
        'success': True,
        'orders': [{
            'id': order.id,
            'order_number': f'#{order.id:06d}',
            'total_amount': order.total_amount,
            'delivery_address': order.delivery_address,
            'distance': 0  # Would be calculated based on delivery person's location
        } for order in available_orders]
    })

@delivery_bp.route('/api/delivery/orders/accept/<int:order_id>', methods=['POST'])
@login_required
@delivery_person_required
def accept_order(order_id):
    """Accept an order for delivery"""
    order = Order.query.get_or_404(order_id)
    
    if order.delivery_person_id is not None:
        return jsonify({
            'success': False,
            'message': 'This order has already been accepted by another delivery person'
        }), 400
    
    order.delivery_person_id = current_user.id
    order.delivery_status = 'in_progress'
    order.status = 'Out for Delivery'
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Order accepted for delivery',
        'order_id': order.id
    })

@delivery_bp.route('/api/delivery/orders/update-location', methods=['POST'])
@login_required
@delivery_person_required
def update_delivery_location():
    """Update the delivery person's current location"""
    data = request.get_json()
    
    if not data or 'order_id' not in data or 'latitude' not in data or 'longitude' not in data:
        return jsonify({
            'success': False,
            'message': 'Missing required fields: order_id, latitude, longitude'
        }), 400
    
    order = Order.query.get(data['order_id'])
    if not order:
        return jsonify({'success': False, 'message': 'Order not found'}), 404
    
    if order.delivery_person_id != current_user.id:
        return jsonify({
            'success': False,
            'message': 'You are not assigned to this order'
        }), 403
    
    order.delivery_person_lat = data['latitude']
    order.delivery_person_lng = data['longitude']
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Location updated',
        'order_id': order.id
    })

@delivery_bp.route('/api/delivery/orders/complete/<int:order_id>', methods=['POST'])
@login_required
@delivery_person_required
def complete_delivery(order_id):
    """Mark an order as delivered"""
    order = Order.query.get_or_404(order_id)
    
    if order.delivery_person_id != current_user.id:
        return jsonify({
            'success': False,
            'message': 'You are not assigned to this order'
        }), 403
    
    order.status = 'Delivered'
    order.delivery_status = 'delivered'
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Order marked as delivered',
        'order_id': order.id
    })

@delivery_bp.route('/api/delivery/orders/my-orders', methods=['GET'])
@login_required
@delivery_person_required
def get_my_orders():
    """Get all orders assigned to the current delivery person"""
    orders = Order.query.filter_by(delivery_person_id=current_user.id).all()
    
    return jsonify({
        'success': True,
        'orders': [{
            'id': order.id,
            'order_number': f'#{order.id:06d}',
            'status': order.status,
            'delivery_status': order.delivery_status,
            'total_amount': order.total_amount,
            'delivery_address': order.delivery_address,
            'customer_lat': order.latitude,
            'customer_lng': order.longitude,
            'delivery_person_lat': order.delivery_person_lat,
            'delivery_person_lng': order.delivery_person_lng,
            'updated_at': order.updated_at.isoformat() if order.updated_at else None
        } for order in orders]
    })
