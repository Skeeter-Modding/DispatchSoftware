// Smyrna Ready Mix Dispatch System - Main JavaScript

// Global variables
let refreshInterval;

// Initialize on page load
$(document).ready(function() {
    // Set today's date in dashboard
    if ($('[data-today]').length) {
        const today = new Date().toLocaleDateString('en-US', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
        $('[data-today]').text(today);
    }
    
    // Auto-refresh for dashboard (30 seconds)
    if ($('#dashboard-refresh').length) {
        startAutoRefresh(30000);
    }
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
});

// Auto-refresh function
function startAutoRefresh(interval) {
    refreshInterval = setInterval(function() {
        // Check if user is still active
        if (document.visibilityState === 'visible') {
            location.reload();
        }
    }, interval);
}

// Stop auto-refresh
function stopAutoRefresh() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }
}

// Load status update function
function updateLoadStatus(loadId, status) {
    return fetch(`/loads/${loadId}/status`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
            status: status,
            timestamp: new Date().toISOString()
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Load status updated successfully', 'success');
            setTimeout(() => location.reload(), 1000);
        } else {
            showNotification('Failed to update load status', 'error');
        }
        return data;
    })
    .catch(error => {
        console.error('Error updating load status:', error);
        showNotification('Error updating load status', 'error');
        throw error;
    });
}

// Show notification function
function showNotification(message, type = 'info') {
    const notification = $('<div>', {
        class: `alert alert-${type} notification-toast`,
        css: {
            position: 'fixed',
            top: '20px',
            right: '20px',
            'z-index': '9999',
            'min-width': '300px',
            'animation': 'slideIn 0.3s ease-out'
        },
        html: `
            <button type="button" class="close" onclick="$(this).parent().fadeOut()">&times;</button>
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'} me-2"></i>
            ${message}
        `
    });
    
    $('body').append(notification);
    
    // Auto-remove after 3 seconds
    setTimeout(() => {
        notification.fadeOut('slow', function() {
            $(this).remove();
        });
    }, 3000);
}

// Confirm action function
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// Format date function
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Format time function
function formatTime(timeString) {
    if (!timeString) return '-';
    const [hours, minutes] = timeString.split(':');
    const hour = parseInt(hours);
    const ampm = hour >= 12 ? 'PM' : 'AM';
    const formattedHour = hour % 12 || 12;
    return `${formattedHour}:${minutes} ${ampm}`;
}

// Calculate time difference
function getTimeDifference(startTime, endTime) {
    const start = new Date(startTime);
    const end = new Date(endTime);
    const diff = end - start;
    
    const hours = Math.floor(diff / 3600000);
    const minutes = Math.floor((diff % 3600000) / 60000);
    
    if (hours > 0) {
        return `${hours}h ${minutes}m`;
    }
    return `${minutes}m`;
}

// Validate form function
function validateForm(formId) {
    const form = $(`#${formId}`);
    const inputs = form.find('input[required], select[required], textarea[required]');
    let isValid = true;
    
    inputs.each(function() {
        if (!$(this).val().trim()) {
            isValid = false;
            $(this).addClass('is-invalid');
        } else {
            $(this).removeClass('is-invalid');
        }
    });
    
    return isValid;
}

// Reset form function
function resetForm(formId) {
    $(`#${formId}`)[0].reset();
    $(`#${formId} .is-invalid`).removeClass('is-invalid');
}

// Export data function
function exportData(data, filename, type = 'csv') {
    let content;
    
    if (type === 'csv') {
        if (Array.isArray(data) && data.length > 0) {
            const headers = Object.keys(data[0]).join(',');
            const rows = data.map(row => Object.values(row).join(','));
            content = [headers, ...rows].join('\n');
        }
    } else if (type === 'json') {
        content = JSON.stringify(data, null, 2);
    }
    
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
}

// Print function
function printElement(elementId) {
    const element = $(`#${elementId}`);
    const contents = element.html();
    
    const printWindow = window.open('', '', 'height=600,width=800');
    printWindow.document.write('<html><head><title>Print</title>');
    printWindow.document.write('<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">');
    printWindow.document.write('</head><body>');
    printWindow.document.write(contents);
    printWindow.document.write('</body></html>');
    printWindow.document.close();
    printWindow.print();
}

// Get current location
function getCurrentLocation() {
    return new Promise((resolve, reject) => {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                position => {
                    resolve({
                        latitude: position.coords.latitude,
                        longitude: position.coords.longitude
                    });
                },
                error => reject(error)
            );
        } else {
            reject(new Error('Geolocation is not supported'));
        }
    });
}

// Calculate distance between two points (Haversine formula)
function calculateDistance(lat1, lon1, lat2, lon2) {
    const R = 6371; // Earth's radius in km
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
              Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
              Math.sin(dLon/2) * Math.sin(dLon/2);
    
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    const distance = R * c;
    
    return distance; // Distance in km
}

// Local storage helpers
function saveToLocalStorage(key, value) {
    try {
        localStorage.setItem(key, JSON.stringify(value));
    } catch (e) {
        console.error('Error saving to local storage:', e);
    }
}

function getFromLocalStorage(key) {
    try {
        const value = localStorage.getItem(key);
        return value ? JSON.parse(value) : null;
    } catch (e) {
        console.error('Error reading from local storage:', e);
        return null;
    }
}

function removeFromLocalStorage(key) {
    try {
        localStorage.removeItem(key);
    } catch (e) {
        console.error('Error removing from local storage:', e);
    }
}

// Debounce function for performance
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Throttle function for performance
function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Mobile detection
function isMobile() {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
}

// Add slide animation to notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
`;
document.head.appendChild(style);

// Close modals on escape key
$(document).on('keydown', function(e) {
    if (e.key === 'Escape') {
        $('.modal.show').modal('hide');
    }
});

// Handle AJAX errors globally
$(document).ajaxError(function(event, jqXHR, settings, thrownError) {
    console.error('AJAX Error:', thrownError);
    if (jqXHR.status === 401) {
        showNotification('Session expired. Please login again.', 'error');
    } else if (jqXHR.status === 500) {
        showNotification('Server error. Please try again later.', 'error');
    }
});

console.log('Smyrna Ready Mix Dispatch System loaded successfully');