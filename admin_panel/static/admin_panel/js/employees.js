// Employee Management JavaScript

$(document).ready(function() {
    AdminPanel.Employees.init();
});

// Extend AdminPanel with Employees module
AdminPanel.Employees = {
    init: function() {
        this.initEmployeeSearch();
        this.initEmployeeActions();
        this.initEmployeeDetails();
        this.initBulkOperations();
    },

    initEmployeeSearch: function() {
        // Enhanced employee search with filters
        $('#employeeSearchForm').on('submit', function(e) {
            e.preventDefault();
            AdminPanel.Employees.performSearch();
        });

        // Real-time search
        $('#employeeSearch').on('input', function() {
            var query = $(this).val().trim();
            if (query.length >= 2) {
                AdminPanel.Employees.liveSearch(query);
            } else {
                $('#employeeSearchResults').hide();
            }
        });

        // Filter changes
        $('.employee-filter').on('change', function() {
            AdminPanel.Employees.applyFilters();
        });
    },

    initEmployeeActions: function() {
        // Toggle employee status
        $(document).on('click', '.toggle-employee-status', function() {
            AdminPanel.Employees.toggleEmployeeStatus($(this));
        });

        // View employee details
        $(document).on('click', '.view-employee-details', function() {
            AdminPanel.Employees.viewEmployeeDetails($(this));
        });

        // Edit employee
        $(document).on('click', '.edit-employee', function() {
            var employeeId = $(this).data('employee-id');
            window.location.href = '/admin-panel/employees/' + employeeId + '/edit/';
        });

        // Delete employee (with confirmation)
        $(document).on('click', '.delete-employee', function() {
            AdminPanel.Employees.deleteEmployee($(this));
        });
    },

    initEmployeeDetails: function() {
        // Load employee details modal
        $('#employeeDetailsModal').on('show.bs.modal', function(event) {
            var button = $(event.relatedTarget);
            var employeeId = button.data('employee-id');
            AdminPanel.Employees.loadEmployeeDetails(employeeId);
        });

        // Employee assignment actions
        $(document).on('click', '.assign-appointment', function() {
            AdminPanel.Employees.assignAppointment($(this));
        });
    },

    initBulkOperations: function() {
        // Bulk employee operations
        $('#employeeBulkForm').on('submit', function(e) {
            e.preventDefault();
            AdminPanel.Employees.performBulkOperation($(this));
        });

        // Select all employees
        $('#selectAllEmployees').on('change', function() {
            $('.employee-checkbox').prop('checked', this.checked);
            AdminPanel.Employees.updateBulkActions();
        });

        // Individual employee selection
        $(document).on('change', '.employee-checkbox', function() {
            AdminPanel.Employees.updateBulkActions();
        });
    },

    performSearch: function() {
        var formData = $('#employeeSearchForm').serialize();
        
        $.ajax({
            url: '/admin-panel/ajax/employees/search/',
            method: 'GET',
            data: formData,
            success: function(response) {
                if (response.success) {
                    AdminPanel.Employees.displaySearchResults(response.employees);
                } else {
                    AdminPanel.Employees.showError('Search failed');
                }
            },
            error: function() {
                AdminPanel.Employees.showError('Error performing search');
            }
        });
    },

    liveSearch: function(query) {
        $.ajax({
            url: '/admin-panel/ajax/employees/search/',
            method: 'GET',
            data: { q: query, limit: 5 },
            success: function(response) {
                if (response.success) {
                    AdminPanel.Employees.displayLiveSearchResults(response.employees);
                }
            }
        });
    },

    displaySearchResults: function(employees) {
        var container = $('#employeeSearchResults');
        container.empty();

        if (employees.length === 0) {
            container.append('<div class="text-muted p-3">No employees found</div>');
        } else {
            employees.forEach(function(employee) {
                var html = AdminPanel.Employees.formatEmployeeCard(employee);
                container.append(html);
            });
        }

        container.show();
    },

    displayLiveSearchResults: function(employees) {
        var dropdown = $('#employeeLiveResults');
        dropdown.empty();

        if (employees.length === 0) {
            dropdown.append('<div class="dropdown-item text-muted">No employees found</div>');
        } else {
            employees.forEach(function(employee) {
                var item = $(`
                    <a class="dropdown-item employee-search-item" href="#" data-employee-id="${employee.id}">
                        <div class="d-flex align-items-center">
                            <div class="employee-avatar me-3">
                                <i class="fas fa-user-circle fa-2x text-secondary"></i>
                            </div>
                            <div>
                                <div class="fw-bold">${employee.name}</div>
                                <small class="text-muted">${employee.specialization} - ${employee.employee_id}</small>
                            </div>
                            <div class="ms-auto">
                                <span class="badge ${employee.is_active ? 'bg-success' : 'bg-secondary'}">
                                    ${employee.is_active ? 'Active' : 'Inactive'}
                                </span>
                            </div>
                        </div>
                    </a>
                `);
                
                item.on('click', function(e) {
                    e.preventDefault();
                    AdminPanel.Employees.viewEmployeeDetails($(this));
                    dropdown.hide();
                });
                
                dropdown.append(item);
            });
        }

        dropdown.show();
    },

    formatEmployeeCard: function(employee) {
        return `
            <div class="col-md-6 col-lg-4 mb-3">
                <div class="card employee-card">
                    <div class="card-body">
                        <div class="d-flex align-items-center mb-3">
                            <div class="employee-avatar me-3">
                                <i class="fas fa-user-circle fa-3x text-secondary"></i>
                            </div>
                            <div class="flex-grow-1">
                                <h6 class="card-title mb-1">${employee.name}</h6>
                                <p class="card-text text-muted mb-0">${employee.employee_id}</p>
                            </div>
                            <div class="employee-status">
                                <span class="badge ${employee.is_active ? 'bg-success' : 'bg-secondary'}">
                                    ${employee.is_active ? 'Active' : 'Inactive'}
                                </span>
                            </div>
                        </div>
                        
                        <div class="employee-info">
                            <p class="mb-1"><strong>Email:</strong> ${employee.email}</p>
                            <p class="mb-1"><strong>Specialization:</strong> ${employee.specialization}</p>
                            ${employee.hire_date ? `<p class="mb-1"><strong>Hire Date:</strong> ${AdminPanel.formatDate(employee.hire_date)}</p>` : ''}
                        </div>
                        
                        <div class="employee-actions mt-3">
                            <button class="btn btn-sm btn-primary view-employee-details" data-employee-id="${employee.id}">
                                <i class="fas fa-eye"></i> View
                            </button>
                            <button class="btn btn-sm btn-outline-primary edit-employee" data-employee-id="${employee.id}">
                                <i class="fas fa-edit"></i> Edit
                            </button>
                            <button class="btn btn-sm ${employee.is_active ? 'btn-outline-warning' : 'btn-outline-success'} toggle-employee-status" 
                                    data-employee-id="${employee.id}" data-current-status="${employee.is_active}">
                                <i class="fas ${employee.is_active ? 'fa-pause' : 'fa-play'}"></i> 
                                ${employee.is_active ? 'Deactivate' : 'Activate'}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    },

    toggleEmployeeStatus: function(button) {
        var employeeId = button.data('employee-id');
        var currentStatus = button.data('current-status');
        var newStatus = !currentStatus;
        var action = newStatus ? 'activate' : 'deactivate';
        
        AdminPanel.Forms.showConfirmDialog(
            'Confirm Status Change',
            `Are you sure you want to ${action} this employee?`,
            function() {
                AdminPanel.showLoading();
                
                $.ajax({
                    url: '/admin-panel/employees/' + employeeId + '/toggle-status/',
                    method: 'POST',
                    data: {
                        csrfmiddlewaretoken: $('[name=csrfmiddlewaretoken]').val()
                    },
                    success: function(response) {
                        if (response.success) {
                            AdminPanel.Employees.showSuccess(response.message);
                            // Update button state
                            button.data('current-status', newStatus);
                            AdminPanel.Employees.updateStatusButton(button, newStatus);
                            // Update status badge
                            AdminPanel.Employees.updateStatusBadge(employeeId, newStatus);
                        } else {
                            AdminPanel.Employees.showError(response.error);
                        }
                    },
                    error: function(xhr) {
                        var message = xhr.responseJSON ? xhr.responseJSON.error : 'Error updating employee status';
                        AdminPanel.Employees.showError(message);
                    },
                    complete: function() {
                        AdminPanel.hideLoading();
                    }
                });
            }
        );
    },

    updateStatusButton: function(button, isActive) {
        button.removeClass('btn-outline-warning btn-outline-success')
              .addClass(isActive ? 'btn-outline-warning' : 'btn-outline-success')
              .html(`<i class="fas ${isActive ? 'fa-pause' : 'fa-play'}"></i> ${isActive ? 'Deactivate' : 'Activate'}`);
    },

    updateStatusBadge: function(employeeId, isActive) {
        var badge = $(`.employee-card[data-employee-id="${employeeId}"] .badge`);
        badge.removeClass('bg-success bg-secondary')
             .addClass(isActive ? 'bg-success' : 'bg-secondary')
             .text(isActive ? 'Active' : 'Inactive');
    },

    viewEmployeeDetails: function(element) {
        var employeeId = element.data('employee-id');
        AdminPanel.Employees.loadEmployeeDetails(employeeId);
    },

    loadEmployeeDetails: function(employeeId) {
        AdminPanel.showLoading();
        
        $.ajax({
            url: '/admin-panel/employees/' + employeeId + '/ajax-detail/',
            method: 'GET',
            success: function(response) {
                if (response.success) {
                    AdminPanel.Employees.displayEmployeeDetails(response.employee);
                } else {
                    AdminPanel.Employees.showError('Failed to load employee details');
                }
            },
            error: function() {
                AdminPanel.Employees.showError('Error loading employee details');
            },
            complete: function() {
                AdminPanel.hideLoading();
            }
        });
    },

    displayEmployeeDetails: function(employee) {
        var modal = $('#employeeDetailsModal');
        
        // Update modal content
        modal.find('.modal-title').text(employee.name);
        
        var detailsHtml = `
            <div class="row">
                <div class="col-md-6">
                    <h6>Personal Information</h6>
                    <table class="table table-sm">
                        <tr><td><strong>Employee ID:</strong></td><td>${employee.employee_id}</td></tr>
                        <tr><td><strong>Email:</strong></td><td>${employee.email}</td></tr>
                        <tr><td><strong>Phone:</strong></td><td>${employee.phone_number || 'N/A'}</td></tr>
                        <tr><td><strong>Address:</strong></td><td>${employee.address || 'N/A'}</td></tr>
                        <tr><td><strong>Hire Date:</strong></td><td>${employee.hire_date ? AdminPanel.formatDate(employee.hire_date) : 'N/A'}</td></tr>
                        <tr><td><strong>Status:</strong></td><td>
                            <span class="badge ${employee.is_active ? 'bg-success' : 'bg-secondary'}">
                                ${employee.is_active ? 'Active' : 'Inactive'}
                            </span>
                        </td></tr>
                    </table>
                </div>
                <div class="col-md-6">
                    <h6>Professional Information</h6>
                    <table class="table table-sm">
                        <tr><td><strong>Specialization:</strong></td><td>${employee.specialization}</td></tr>
                        <tr><td><strong>Total Appointments:</strong></td><td>${employee.total_appointments}</td></tr>
                        <tr><td><strong>Completed Appointments:</strong></td><td>${employee.completed_appointments}</td></tr>
                        <tr><td><strong>Average Rating:</strong></td><td>${employee.average_rating || 'N/A'}</td></tr>
                    </table>
                </div>
            </div>
        `;
        
        if (employee.recent_appointments && employee.recent_appointments.length > 0) {
            detailsHtml += `
                <div class="mt-4">
                    <h6>Recent Appointments</h6>
                    <div class="table-responsive">
                        <table class="table table-sm">
                            <thead>
                                <tr>
                                    <th>Date</th>
                                    <th>Service</th>
                                    <th>Customer</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody>
            `;
            
            employee.recent_appointments.forEach(function(appointment) {
                detailsHtml += `
                    <tr>
                        <td>${AdminPanel.formatDate(appointment.appointment_date)}</td>
                        <td>${appointment.service_name}</td>
                        <td>${appointment.customer_name}</td>
                        <td><span class="badge bg-${AdminPanel.Employees.getStatusColor(appointment.status)}">${appointment.status}</span></td>
                    </tr>
                `;
            });
            
            detailsHtml += `
                            </tbody>
                        </table>
                    </div>
                </div>
            `;
        }
        
        modal.find('.modal-body').html(detailsHtml);
        
        // Update modal footer with action buttons
        var footerHtml = `
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
            <a href="/admin-panel/employees/${employee.id}/edit/" class="btn btn-primary">Edit Employee</a>
        `;
        modal.find('.modal-footer').html(footerHtml);
        
        modal.modal('show');
    },

    getStatusColor: function(status) {
        switch (status.toLowerCase()) {
            case 'completed': return 'success';
            case 'confirmed': return 'info';
            case 'pending': return 'warning';
            case 'cancelled': return 'danger';
            default: return 'secondary';
        }
    },

    deleteEmployee: function(button) {
        var employeeId = button.data('employee-id');
        var employeeName = button.data('employee-name') || 'this employee';
        
        AdminPanel.Forms.showConfirmDialog(
            'Delete Employee',
            `Are you sure you want to delete ${employeeName}? This action cannot be undone.`,
            function() {
                AdminPanel.showLoading();
                
                $.ajax({
                    url: '/admin-panel/employees/' + employeeId + '/delete/',
                    method: 'POST',
                    data: {
                        csrfmiddlewaretoken: $('[name=csrfmiddlewaretoken]').val()
                    },
                    success: function(response) {
                        if (response.success) {
                            AdminPanel.Employees.showSuccess(response.message);
                            // Remove employee card from view
                            $(`.employee-card[data-employee-id="${employeeId}"]`).fadeOut();
                        } else {
                            AdminPanel.Employees.showError(response.error);
                        }
                    },
                    error: function(xhr) {
                        var message = xhr.responseJSON ? xhr.responseJSON.error : 'Error deleting employee';
                        AdminPanel.Employees.showError(message);
                    },
                    complete: function() {
                        AdminPanel.hideLoading();
                    }
                });
            }
        );
    },

    performBulkOperation: function(form) {
        var formData = form.serialize();
        var selectedEmployees = $('.employee-checkbox:checked').length;
        
        if (selectedEmployees === 0) {
            AdminPanel.Employees.showError('Please select at least one employee');
            return;
        }
        
        AdminPanel.Forms.showConfirmDialog(
            'Confirm Bulk Operation',
            `Are you sure you want to perform this operation on ${selectedEmployees} employee(s)?`,
            function() {
                AdminPanel.showLoading();
                
                $.ajax({
                    url: '/admin-panel/employees/bulk-action/',
                    method: 'POST',
                    data: formData,
                    success: function(response) {
                        if (response.success) {
                            AdminPanel.Employees.showSuccess(response.message);
                            location.reload(); // Refresh the page to show changes
                        } else {
                            AdminPanel.Employees.showError(response.error);
                        }
                    },
                    error: function(xhr) {
                        var message = xhr.responseJSON ? xhr.responseJSON.error : 'Error performing bulk operation';
                        AdminPanel.Employees.showError(message);
                    },
                    complete: function() {
                        AdminPanel.hideLoading();
                    }
                });
            }
        );
    },

    updateBulkActions: function() {
        var checkedCount = $('.employee-checkbox:checked').length;
        var bulkActions = $('.bulk-actions');
        
        if (checkedCount > 0) {
            bulkActions.removeClass('d-none');
            $('.bulk-count').text(checkedCount);
        } else {
            bulkActions.addClass('d-none');
        }
        
        // Update select all checkbox state
        var totalCheckboxes = $('.employee-checkbox').length;
        var selectAllCheckbox = $('#selectAllEmployees');
        
        if (checkedCount === 0) {
            selectAllCheckbox.prop('indeterminate', false).prop('checked', false);
        } else if (checkedCount === totalCheckboxes) {
            selectAllCheckbox.prop('indeterminate', false).prop('checked', true);
        } else {
            selectAllCheckbox.prop('indeterminate', true).prop('checked', false);
        }
    },

    applyFilters: function() {
        var filters = {};
        $('.employee-filter').each(function() {
            var name = $(this).attr('name');
            var value = $(this).val();
            if (value) {
                filters[name] = value;
            }
        });
        
        // Apply filters to current page
        var currentUrl = new URL(window.location);
        Object.keys(filters).forEach(function(key) {
            currentUrl.searchParams.set(key, filters[key]);
        });
        
        // Remove empty filters
        $('.employee-filter').each(function() {
            var name = $(this).attr('name');
            if (!$(this).val()) {
                currentUrl.searchParams.delete(name);
            }
        });
        
        window.location.href = currentUrl.toString();
    },

    showSuccess: function(message) {
        AdminPanel.showAlert('success', message);
    },

    showError: function(message) {
        AdminPanel.showAlert('danger', message);
    }
};

// Helper function to show alerts (if not already defined)
if (typeof AdminPanel.showAlert === 'undefined') {
    AdminPanel.showAlert = function(type, message) {
        var alertHtml = '<div class="alert alert-' + type + ' alert-dismissible fade show" role="alert">' +
                       message +
                       '<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>' +
                       '</div>';
        
        $('.main-content .container-fluid').prepend(alertHtml);
        
        // Auto-hide after 5 seconds
        setTimeout(function() {
            $('.alert').fadeOut('slow');
        }, 5000);
    };
}