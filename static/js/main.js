// CarModX Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
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

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Auto-hide alerts after 5 seconds - DISABLED
    // Users can manually close alerts using the close button
    // setTimeout(function() {
    //     var alerts = document.querySelectorAll('.alert');
    //     alerts.forEach(function(alert) {
    //         var bsAlert = new bootstrap.Alert(alert);
    //         bsAlert.close();
    //     });
    // }, 5000);

    // Form validation enhancement (disabled for now)
    // const forms = document.querySelectorAll('.needs-validation');
    // Array.from(forms).forEach(form => {
    //     form.addEventListener('submit', event => {
    //         if (!form.checkValidity()) {
    //             event.preventDefault();
    //             event.stopPropagation();
    //         }
    //         form.classList.add('was-validated');
    //     });
    // });

    // Loading state for buttons (disabled for now - handled per form)
    // document.querySelectorAll('button[type="submit"]').forEach(button => {
    //     button.addEventListener('click', function(e) {
    //         // Only show loading if form is valid
    //         if (this.form && this.form.checkValidity()) {
    //             this.innerHTML = '<span class="loading"></span> Processing...';
    //             this.disabled = true;
    //             // Re-enable button after 10 seconds as fallback
    //             setTimeout(() => {
    //                 this.disabled = false;
    //                 this.innerHTML = this.getAttribute('data-original-text') || 'Submit';
    //             }, 10000);
    //         }
    //     });
    // });

    // Dynamic time slot loading
    const dateInput = document.getElementById('id_date');
    if (dateInput) {
        dateInput.addEventListener('change', function() {
            loadTimeSlots(this.value);
        });
    }

    // Search functionality
    const searchInput = document.getElementById('search');
    if (searchInput) {
        let searchTimeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                performSearch(this.value);
            }, 300);
        });
    }

    // Image lazy loading
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });

        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    }
});

// Load time slots for selected date
function loadTimeSlots(date) {
    if (!date) return;
    
    const timeSlotContainer = document.getElementById('time-slots');
    if (!timeSlotContainer) return;

    // Show loading state
    timeSlotContainer.innerHTML = '<div class="text-center"><div class="spinner-border" role="status"><span class="visually-hidden">Loading...</span></div></div>';

    // Make AJAX request to load time slots
    fetch(`/appointments/api/time-slots/?date=${date}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                renderTimeSlots(data.time_slots);
            } else {
                timeSlotContainer.innerHTML = '<div class="alert alert-warning">No available time slots for this date.</div>';
            }
        })
        .catch(error => {
            console.error('Error loading time slots:', error);
            timeSlotContainer.innerHTML = '<div class="alert alert-danger">Error loading time slots. Please try again.</div>';
        });
}

// Render time slots
function renderTimeSlots(timeSlots) {
    const container = document.getElementById('time-slots');
    if (!container) return;

    if (timeSlots.length === 0) {
        container.innerHTML = '<div class="alert alert-warning">No available time slots for this date.</div>';
        return;
    }

    let html = '<div class="row">';
    timeSlots.forEach(slot => {
        html += `
            <div class="col-md-6 mb-3">
                <div class="card time-slot-card">
                    <div class="card-body">
                        <div class="form-check">
                            <input class="form-check-input" type="radio" name="time_slot" value="${slot.id}" id="slot-${slot.id}">
                            <label class="form-check-label" for="slot-${slot.id}">
                                <strong>${slot.start_time} - ${slot.end_time}</strong>
                                <br>
                                <small class="text-muted">${slot.remaining_slots} slot(s) available</small>
                            </label>
                        </div>
                    </div>
                </div>
            </div>
        `;
    });
    html += '</div>';
    
    container.innerHTML = html;
}

// Perform search
function performSearch(query) {
    if (query.length < 2) return;
    
    // This would typically make an AJAX request to search endpoints
    console.log('Searching for:', query);
}

// Format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

// Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

// Format time
function formatTime(timeString) {
    const time = new Date(`2000-01-01T${timeString}`);
    return time.toLocaleTimeString('en-US', {
        hour: 'numeric',
        minute: '2-digit',
        hour12: true
    });
}

// Show notification
function showNotification(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alertDiv);
            bsAlert.close();
        }, 5000);
    }
}

// Confirm action
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// Copy to clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Copied to clipboard!', 'success');
    }).catch(err => {
        console.error('Failed to copy: ', err);
        showNotification('Failed to copy to clipboard', 'danger');
    });
}

// Export functions to global scope
window.CarModX = {
    loadTimeSlots,
    renderTimeSlots,
    performSearch,
    formatCurrency,
    formatDate,
    formatTime,
    showNotification,
    confirmAction,
    copyToClipboard
};
