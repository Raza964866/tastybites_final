// Cart functionality for TastyBites

// Initialize cart from backend session or create empty cart
let cart = [];
let cartTotal = 0;

// Load cart from backend session
function loadCartFromSession() {
    return fetch('/api/cart', {
        method: 'GET',
        credentials: 'same-origin'
    })
    .then(response => response.json())
    .then(data => {
        cart = data.cart || [];
        updateCartDisplay();
        updateCartCount();
    })
    .catch(error => {
        console.error('Error loading cart:', error);
        cart = [];
        updateCartDisplay();
        updateCartCount();
    });
}

// Update cart count in the header
function updateCartCount() {
    const cartCountElement = document.getElementById('cart-count');
    if (cartCountElement) {
        const itemCount = cart.reduce((total, item) => total + item.quantity, 0);
        cartCountElement.textContent = itemCount;
    }
}

// Update cart display
function updateCartDisplay() {
    const cartItemsElement = document.getElementById('cart-items');
    const placeOrderBtn = document.getElementById('place-order-btn');
    const emptyCartMessage = `
        <div class="empty-cart-message">
            <i class="fas fa-shopping-cart"></i>
            <p>Your cart is empty</p>
            <a href="#menu" class="btn btn-primary">Browse Menu</a>
        </div>
    `;
    
    if (!cartItemsElement) return;
    
    // Clear current cart display
    cartItemsElement.innerHTML = '';
    
    if (cart.length === 0) {
        cartItemsElement.innerHTML = emptyCartMessage;
        const subtotalElement = document.getElementById('cart-subtotal');
        const taxElement = document.getElementById('cart-tax');
        const totalElement = document.getElementById('cart-total');
        
        if (subtotalElement) subtotalElement.textContent = '$0.00';
        if (taxElement) taxElement.textContent = '$0.00';
        if (totalElement) totalElement.textContent = '$0.00';
        
        // Disable place order button
        if (placeOrderBtn) {
            placeOrderBtn.disabled = true;
        }
        
        // Update cart count in header
        updateCartCount();
        return;
    }
    
    // Calculate subtotal, tax, and total
    let subtotal = 0;
    
    // Create cart items
    cart.forEach((item, index) => {
        const itemTotal = item.price * item.quantity;
        subtotal += itemTotal;
        
        const cartItemElement = document.createElement('div');
        cartItemElement.className = 'cart-item';
        cartItemElement.innerHTML = `
            <div class="cart-item-details">
                <div class="cart-item-name">${item.name}</div>
                <div class="cart-item-price">$${item.price.toFixed(2)} each</div>
                <div class="cart-item-actions">
                    <button class="btn btn-sm btn-outline-secondary decrease-qty" data-index="${index}">
                        <i class="fas fa-minus"></i>
                    </button>
                    <span class="quantity">${item.quantity}</span>
                    <button class="btn btn-sm btn-outline-secondary increase-qty" data-index="${index}">
                        <i class="fas fa-plus"></i>
                    </button>
                    <button class="btn btn-sm btn-link text-danger remove-item" data-index="${index}">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
            <div class="cart-item-total">$${itemTotal.toFixed(2)}</div>
        `;
        
        // Add event listeners for buttons
        const decreaseBtn = cartItemElement.querySelector('.decrease-qty');
        const increaseBtn = cartItemElement.querySelector('.increase-qty');
        const removeBtn = cartItemElement.querySelector('.remove-item');
        
        decreaseBtn.addEventListener('click', (event) => decreaseQuantity(index, event));
        increaseBtn.addEventListener('click', (event) => increaseQuantity(index, event));
        removeBtn.addEventListener('click', (event) => removeFromCart(index, event));
        
        cartItemsElement.appendChild(cartItemElement);
    });
    
    // Calculate tax (10% of subtotal)
    const tax = subtotal * 0.1;
    const total = subtotal + tax;
    
    // Update total display
    const subtotalElement = document.getElementById('cart-subtotal');
    const taxElement = document.getElementById('cart-tax');
    const totalElement = document.getElementById('cart-total');
    
    if (subtotalElement) subtotalElement.textContent = `$${subtotal.toFixed(2)}`;
    if (taxElement) taxElement.textContent = `$${tax.toFixed(2)}`;
    if (totalElement) totalElement.textContent = `$${total.toFixed(2)}`;
    
    // Enable place order button
    if (placeOrderBtn) {
        placeOrderBtn.disabled = false;
    }
    
    // Save cart to localStorage
    saveCart();
    
    // Update cart count in header
    updateCartCount();
}

// Add item to cart
function addToCart(id, name, price) {
    // Send add to cart request to backend
    fetch('/api/cart/add', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('meta[name="csrf-token"]')?.content || ''
        },
        body: JSON.stringify({
            id: parseInt(id),
            name: name,
            price: parseFloat(price)
        }),
        credentials: 'same-origin'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            cart = data.cart || [];
            updateCartDisplay();
            showNotification(`${name} added to cart!`);
        } else {
            showNotification('Failed to add item to cart', 'danger');
        }
    })
    .catch(error => {
        console.error('Error adding item to cart:', error);
        showNotification('Error adding item to cart', 'danger');
    });
}

// Remove item from cart
function removeFromCart(index, event) {
    if (event) {
        event.preventDefault();
        event.stopPropagation();
    }
    
    if (index >= 0 && index < cart.length) {
        const removedItem = cart[index];
        
        // Send remove request to backend
        fetch('/api/cart/remove', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('meta[name="csrf-token"]')?.content || ''
            },
            body: JSON.stringify({
                id: removedItem.id
            }),
            credentials: 'same-origin'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                cart = data.cart || [];
                updateCartDisplay();
                showNotification(`${removedItem.name} removed from cart`, 'warning');
            } else {
                showNotification('Failed to remove item from cart', 'danger');
            }
        })
        .catch(error => {
            console.error('Error removing item from cart:', error);
            showNotification('Error removing item from cart', 'danger');
        });
    }
}

// Increase item quantity
function increaseQuantity(index, event) {
    if (event) event.preventDefault();
    if (index >= 0 && index < cart.length) {
        const item = cart[index];
        const newQuantity = item.quantity + 1;
        
        // Update quantity via backend
        fetch('/api/cart/update', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('meta[name="csrf-token"]')?.content || ''
            },
            body: JSON.stringify({
                id: item.id,
                quantity: newQuantity
            }),
            credentials: 'same-origin'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                cart = data.cart || [];
                updateCartDisplay();
                showNotification(`Increased quantity of ${item.name}`, 'success');
            } else {
                showNotification('Failed to update quantity', 'danger');
            }
        })
        .catch(error => {
            console.error('Error updating quantity:', error);
            showNotification('Error updating quantity', 'danger');
        });
    }
}

// Decrease item quantity
function decreaseQuantity(index, event) {
    if (event) event.preventDefault();
    if (index >= 0 && index < cart.length) {
        const item = cart[index];
        
        if (item.quantity > 1) {
            const newQuantity = item.quantity - 1;
            
            // Update quantity via backend
            fetch('/api/cart/update', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('meta[name="csrf-token"]')?.content || ''
                },
                body: JSON.stringify({
                    id: item.id,
                    quantity: newQuantity
                }),
                credentials: 'same-origin'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    cart = data.cart || [];
                    updateCartDisplay();
                    showNotification(`Decreased quantity of ${item.name}`, 'info');
                } else {
                    showNotification('Failed to update quantity', 'danger');
                }
            })
            .catch(error => {
                console.error('Error updating quantity:', error);
                showNotification('Error updating quantity', 'danger');
            });
        } else {
            removeFromCart(index, event);
        }
    }
}

// Save cart to localStorage
function saveCart() {
    localStorage.setItem('cart', JSON.stringify(cart));
}

// Clear cart
function clearCart() {
    // Send clear cart request to backend
    fetch('/api/cart/clear', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('meta[name="csrf-token"]')?.content || ''
        },
        credentials: 'same-origin'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            cart = [];
            updateCartDisplay();
            showNotification('Cart cleared');
        } else {
            showNotification('Failed to clear cart', 'danger');
        }
    })
    .catch(error => {
        console.error('Error clearing cart:', error);
        showNotification('Error clearing cart', 'danger');
    });
}

// Show notification
function showNotification(message, type = 'info', duration = 3000) {
    // Create notification element if it doesn't exist
    let notification = document.getElementById('cart-notification');
    
    if (!notification) {
        notification = document.createElement('div');
        notification.id = 'cart-notification';
        document.body.appendChild(notification);
    }
    
    // Set message and show notification
    notification.textContent = message;
    notification.className = 'show';
    
    // Hide notification after 3 seconds
    setTimeout(() => {
        notification.className = '';
    }, 3000);
}

// Place order
function placeOrder() {
    // Disable the place order button to prevent multiple submissions
    const placeOrderBtn = document.getElementById('place-order-btn');
    if (placeOrderBtn) {
        placeOrderBtn.disabled = true;
        placeOrderBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Placing Order...';
    }

    if (cart.length === 0) {
        showNotification('Your cart is empty', 'warning');
        if (placeOrderBtn) {
            placeOrderBtn.disabled = false;
            placeOrderBtn.textContent = 'Place Order';
        }
        return;
    }
    
    // Show loading state
    const notification = showNotification('Processing your order...', 'info', 0);
    
    // Check if user is logged in
    fetch('/api/check-auth')
        .then(response => {
            if (!response.ok) throw new Error('Network response was not ok');
            return response.json();
        })
        .then(data => {
            if (!data.authenticated) {
                // Save cart to session before redirecting to login
                return fetch('/api/cart/save', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('meta[name="csrf-token"]')?.content || ''
                    },
                    body: JSON.stringify({ cart: cart })
                }).then(() => {
                    // Redirect to login with next parameter
                    window.location.href = '/login?next=' + encodeURIComponent(window.location.pathname);
                    throw new Error('Not authenticated');
                });
            }
            
            // Prepare order data with validation
            const orderItems = [];
            for (const item of cart) {
                if (!item.id || !item.name || !item.price || !item.quantity) {
                    throw new Error('Invalid cart item data');
                }
                
                orderItems.push({
                    id: parseInt(item.id),
                    name: item.name,
                    price: parseFloat(item.price),
                    quantity: parseInt(item.quantity)
                });
            }
            
            // Submit order to backend
            return fetch('/api/order/create', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('meta[name="csrf-token"]')?.content || ''
                },
                body: JSON.stringify({ items: orderItems }),
                credentials: 'same-origin'
            });
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => {
                    throw new Error(err.message || 'Failed to place order');
                });
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                // Show success message
                showNotification('Order placed successfully!', 'success');
                
                // Clear cart locally (backend already cleared it)
                cart = [];
                updateCartDisplay();
                
                // Redirect to order confirmation page
                if (data.redirect) {
                    window.location.href = data.redirect;
                } else if (data.order_id) {
                    window.location.href = `/receipt/${data.order_id}`;
                } else {
                    window.location.href = '/profile';
                }
            } else {
                throw new Error(data.message || 'Failed to place order');
            }
        })
        .catch(error => {
            console.error('Order error:', error);
            showNotification(error.message || 'An error occurred while placing your order. Please try again.', 'danger');
            
            // Re-enable the place order button
            if (placeOrderBtn) {
                placeOrderBtn.disabled = false;
                placeOrderBtn.textContent = 'Place Order';
            }
            
            // Remove loading notification
            if (notification) {
                notification.remove();
            }
        });
}

// Enhanced showNotification function
function showNotification(message, type = 'info', duration = 3000) {
    // Remove any existing notifications
    const existingNotifications = document.querySelectorAll('.custom-notification');
    existingNotifications.forEach(notification => notification.remove());
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `custom-notification alert alert-${type} alert-dismissible fade show`;
    notification.role = 'alert';
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '9999';
    notification.style.minWidth = '300px';
    notification.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
    
    // Create message text node
    const messageNode = document.createTextNode(message);
    notification.appendChild(messageNode);
    
    // Create close button
    const closeBtn = document.createElement('button');
    closeBtn.type = 'button';
    closeBtn.className = 'btn-close';
    closeBtn.setAttribute('data-bs-dismiss', 'alert');
    closeBtn.setAttribute('aria-label', 'Close');
    notification.appendChild(closeBtn);
    
    // Add to document
    document.body.appendChild(notification);
    
    // Auto-remove after duration if duration is not 0
    if (duration > 0) {
        setTimeout(() => {
            notification.classList.remove('show');
            notification.classList.add('fade');
            setTimeout(() => notification.remove(), 150);
        }, duration);
    }
    
    // Handle manual close
    closeBtn.addEventListener('click', () => {
        notification.classList.remove('show');
        notification.classList.add('fade');
        setTimeout(() => notification.remove(), 150);
    });
    
    // Show with animation
    setTimeout(() => notification.classList.add('show'), 10);
    
    return notification;
}

// Initialize cart on page load
document.addEventListener('DOMContentLoaded', function() {
    loadCartFromSession();
});
