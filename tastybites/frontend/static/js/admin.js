// Admin Panel JavaScript

// Toggle sidebar on mobile
document.addEventListener('DOMContentLoaded', function() {
    // Toggle sidebar
    document.getElementById('sidebarCollapse').addEventListener('click', function() {
        document.getElementById('sidebar').classList.toggle('active');
    });

    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    var alerts = document.querySelectorAll('.alert.alert-dismissible');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
});

// Update order status
function updateOrderStatus(orderId, newStatus) {
    if (!confirm('Are you sure you want to update the order status?')) {
        // Reset the select to its previous value
        event.target.value = event.target.dataset.currentStatus;
        return;
    }

    fetch(`/admin/orders/update-status/${orderId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
        },
        body: `status=${encodeURIComponent(newStatus)}`
    })
    .then(response => {
        if (response.redirected) {
            window.location.href = response.url;
        } else {
            return response.json();
        }
    })
    .then(data => {
        if (data && data.success) {
            // Update the status badge
            const statusBadge = document.querySelector(`#order-${orderId}-status`);
            if (statusBadge) {
                statusBadge.className = `badge bg-${getStatusBadgeClass(newStatus)}`;
                statusBadge.textContent = newStatus;
            }
            
            // Show success message
            showAlert('Order status updated successfully!', 'success');
        } else {
            throw new Error('Failed to update order status');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('Failed to update order status. Please try again.', 'danger');
        // Reset the select to its previous value
        event.target.value = event.target.dataset.currentStatus;
    });
}

// Helper function to get badge class based on status
function getStatusBadgeClass(status) {
    const statusMap = {
        'Pending': 'warning',
        'Confirmed': 'info',
        'Preparing': 'primary',
        'Ready': 'success',
        'Delivered': 'success',
        'Cancelled': 'danger'
    };
    return statusMap[status] || 'secondary';
}

// Export data
function exportData(type, format) {
    const params = new URLSearchParams(window.location.search);
    let url = `/admin/export/${type}.${format}?${params.toString()}`;
    window.location.href = url;
}

// Print order
function printSection(sectionId) {
    const printContent = document.getElementById(sectionId);
    const printWindow = window.open('', '', 'width=800,height=600');
    
    printWindow.document.write(`
        <html>
            <head>
                <title>Print Order</title>
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
                <style>
                    @media print {
                        @page { margin: 0; }
                        body { margin: 1.6cm; }
                        .no-print { display: none !important; }
                    }
                </style>
            </head>
            <body>
                ${printContent.innerHTML}
                <div class="no-print text-center mt-4">
                    <button class="btn btn-primary" onclick="window.print()">Print</button>
                    <button class="btn btn-secondary ms-2" onclick="window.close()">Close</button>
                </div>
                <script>
                    // Auto-print when the window loads
                    window.onload = function() {
                        setTimeout(function() {
                            window.print();
                        }, 200);
                    };
                <\/script>
            </body>
        </html>
    `);
    
    printWindow.document.close();
}

// Show alert message
function showAlert(message, type = 'info') {
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    
    // Prepend alert to the content area
    const content = document.querySelector('.container-fluid');
    if (content) {
        content.insertAdjacentHTML('afterbegin', alertHtml);
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            const alert = document.querySelector('.alert');
            if (alert) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, 5000);
    }
}

// Initialize DataTables if available
if (typeof $ !== 'undefined' && $.fn.DataTable) {
    $(document).ready(function() {
        $('.datatable').DataTable({
            responsive: true,
            order: [[0, 'desc']],
            pageLength: 25,
            language: {
                search: "_INPUT_",
                searchPlaceholder: "Search..."
            },
            dom: "<'row'<'col-sm-12 col-md-6'l><'col-sm-12 col-md-6'f>>" +
                 "<'row'<'col-sm-12'tr>>" +
                 "<'row'<'col-sm-12 col-md-5'i><'col-sm-12 col-md-7'p>>"
        });
    });
}
