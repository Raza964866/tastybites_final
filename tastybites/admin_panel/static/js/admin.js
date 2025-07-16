// Admin Panel JavaScript

// Sidebar toggle
document.addEventListener('DOMContentLoaded', function() {
    const sidebarCollapse = document.getElementById('sidebarCollapse');
    const sidebar = document.getElementById('sidebar');
    const content = document.getElementById('content');
    
    if (sidebarCollapse) {
        sidebarCollapse.addEventListener('click', function() {
            sidebar.classList.toggle('active');
            content.classList.toggle('active');
        });
    }
    
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bootstrapAlert = new bootstrap.Alert(alert);
            bootstrapAlert.close();
        }, 5000);
    });
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    const popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // File upload preview
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(function(input) {
        input.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    let preview = document.getElementById('image-preview');
                    if (!preview) {
                        preview = document.createElement('img');
                        preview.id = 'image-preview';
                        preview.className = 'image-preview';
                        input.parentNode.appendChild(preview);
                    }
                    preview.src = e.target.result;
                };
                reader.readAsDataURL(file);
            }
        });
    });
    
    // Confirm delete actions
    const deleteButtons = document.querySelectorAll('.btn-delete');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item?')) {
                e.preventDefault();
                return false;
            }
        });
    });
    
    // Live search functionality
    const searchInputs = document.querySelectorAll('.live-search');
    searchInputs.forEach(function(input) {
        let timeout;
        input.addEventListener('input', function() {
            clearTimeout(timeout);
            timeout = setTimeout(function() {
                const searchTerm = input.value;
                const targetTable = document.querySelector(input.dataset.target);
                if (targetTable) {
                    filterTable(targetTable, searchTerm);
                }
            }, 300);
        });
    });
    
    // Auto-refresh dashboard stats
    if (document.querySelector('.dashboard-stats')) {
        setInterval(updateDashboardStats, 60000); // Update every minute
    }
});

// Filter table rows based on search term
function filterTable(table, searchTerm) {
    const rows = table.querySelectorAll('tbody tr');
    rows.forEach(function(row) {
        const text = row.textContent.toLowerCase();
        if (text.includes(searchTerm.toLowerCase())) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

// Update dashboard statistics
function updateDashboardStats() {
    fetch('/admin/api/stats')
        .then(response => response.json())
        .then(data => {
            // Update stat cards
            updateStatCard('total-users', data.total_users);
            updateStatCard('total-menu-items', data.total_menu_items);
            updateStatCard('total-orders', data.total_orders);
            updateStatCard('pending-orders', data.pending_orders);
            updateStatCard('total-revenue', '$' + data.total_revenue.toFixed(2));
        })
        .catch(error => {
            console.error('Error updating dashboard stats:', error);
        });
}

// Update individual stat card
function updateStatCard(id, value) {
    const element = document.getElementById(id);
    if (element) {
        element.textContent = value;
        // Add animation class
        element.classList.add('updated');
        setTimeout(function() {
            element.classList.remove('updated');
        }, 1000);
    }
}

// Show loading spinner
function showLoading(element) {
    element.innerHTML = '<div class="spinner-border spinner-border-sm" role="status"><span class="visually-hidden">Loading...</span></div>';
    element.disabled = true;
}

// Hide loading spinner
function hideLoading(element, originalText) {
    element.innerHTML = originalText;
    element.disabled = false;
}

// Format currency
function formatCurrency(amount) {
    return '$' + parseFloat(amount).toFixed(2);
}

// Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

// Show notification
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show`;
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container-fluid');
    container.insertBefore(notification, container.firstChild);
    
    // Auto-hide after 5 seconds
    setTimeout(function() {
        const bootstrapAlert = new bootstrap.Alert(notification);
        bootstrapAlert.close();
    }, 5000);
}

// AJAX form submission
function submitForm(form, callback) {
    const formData = new FormData(form);
    const submitButton = form.querySelector('button[type="submit"]');
    const originalText = submitButton.innerHTML;
    
    showLoading(submitButton);
    
    fetch(form.action, {
        method: form.method,
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        hideLoading(submitButton, originalText);
        if (data.success) {
            showNotification(data.message, 'success');
            if (callback) callback(data);
        } else {
            showNotification(data.message, 'danger');
        }
    })
    .catch(error => {
        hideLoading(submitButton, originalText);
        showNotification('An error occurred. Please try again.', 'danger');
        console.error('Error:', error);
    });
}

// Order status update
function updateOrderStatus(orderId, newStatus) {
    if (confirm('Are you sure you want to update this order status?')) {
        const formData = new FormData();
        formData.append('status', newStatus);
        
        fetch(`/admin/orders/update-status/${orderId}`, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                throw new Error('Network response was not ok');
            }
        })
        .then(data => {
            if (data.success) {
                showNotification(data.message, 'success');
                location.reload();
            } else {
                showNotification(data.message, 'danger');
            }
        })
        .catch(error => {
            showNotification('Error updating order status', 'danger');
            console.error('Error:', error);
        });
    }
}

// Export data functionality
function exportData(type, format = 'csv') {
    const url = `/admin/export/${type}?format=${format}`;
    window.open(url, '_blank');
}

// Print functionality
function printSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
        const printWindow = window.open('', '', 'width=800,height=600');
        printWindow.document.write(`
            <html>
                <head>
                    <title>Print</title>
                    <style>
                        body { font-family: Arial, sans-serif; }
                        table { width: 100%; border-collapse: collapse; }
                        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                        th { background-color: #f2f2f2; }
                    </style>
                </head>
                <body>
                    ${section.innerHTML}
                </body>
            </html>
        `);
        printWindow.document.close();
        printWindow.print();
    }
}

// Chart initialization (if Chart.js is loaded)
if (typeof Chart !== 'undefined') {
    // Initialize charts when DOM is ready
    document.addEventListener('DOMContentLoaded', function() {
        initializeCharts();
    });
}

function initializeCharts() {
    // Revenue chart
    const revenueChart = document.getElementById('revenueChart');
    if (revenueChart) {
        new Chart(revenueChart, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    label: 'Revenue',
                    data: [1200, 1900, 3000, 5000, 2000, 3000],
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }
    
    // Orders chart
    const ordersChart = document.getElementById('ordersChart');
    if (ordersChart) {
        new Chart(ordersChart, {
            type: 'doughnut',
            data: {
                labels: ['Pending', 'Completed', 'Cancelled'],
                datasets: [{
                    data: [12, 19, 3],
                    backgroundColor: [
                        'rgba(255, 206, 86, 0.8)',
                        'rgba(75, 192, 192, 0.8)',
                        'rgba(255, 99, 132, 0.8)'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }
}

// Admin JS