// Admin Panel JavaScript

$(document).ready(function() {
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
    setTimeout(function() {
        $('.alert').fadeOut('slow');
    }, 5000);

    // Initialize enhanced functionality
    AdminPanel.Search.init();
    AdminPanel.Forms.init();
    AdminPanel.Dashboard.init();
    AdminPanel.Notifications.init();

    // Confirm delete actions
    $('.btn-delete').on('click', function(e) {
        e.preventDefault();
        var url = $(this).attr('href');
        var itemName = $(this).data('item-name') || 'this item';
        
        if (confirm('Are you sure you want to delete ' + itemName + '? This action cannot be undone.')) {
            window.location.href = url;
        }
    });

    // Form validation feedback
    $('.needs-validation').on('submit', function(e) {
        if (!this.checkValidity()) {
            e.preventDefault();
            e.stopPropagation();
        }
        $(this).addClass('was-validated');
    });

    // Search functionality
    $('#searchInput').on('keyup', function() {
        var value = $(this).val().toLowerCase();
        $('#dataTable tbody tr').filter(function() {
            $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1);
        });
    });

    // Bulk actions
    $('#selectAll').on('change', function() {
        $('.item-checkbox').prop('checked', this.checked);
        updateBulkActions();
    });

    $('.item-checkbox').on('change', function() {
        updateBulkActions();
    });

    function updateBulkActions() {
        var checkedCount = $('.item-checkbox:checked').length;
        if (checkedCount > 0) {
            $('.bulk-actions').removeClass('d-none');
            $('.bulk-count').text(checkedCount);
        } else {
            $('.bulk-actions').addClass('d-none');
        }
    }

    // AJAX form submissions
    $('.ajax-form').on('submit', function(e) {
        e.preventDefault();
        var form = $(this);
        var url = form.attr('action');
        var method = form.attr('method') || 'POST';
        var submitBtn = form.find('button[type="submit"]');
        var originalText = submitBtn.html();

        // Show loading state
        submitBtn.html('<span class="spinner-border spinner-border-sm me-2" role="status"></span>Loading...');
        submitBtn.prop('disabled', true);

        $.ajax({
            url: url,
            method: method,
            data: form.serialize(),
            success: function(response) {
                if (response.success) {
                    showAlert('success', response.message || 'Operation completed successfully');
                    if (response.redirect) {
                        window.location.href = response.redirect;
                    } else {
                        location.reload();
                    }
                } else {
                    showAlert('danger', response.message || 'An error occurred');
                }
            },
            error: function(xhr) {
                var message = 'An error occurred';
                if (xhr.responseJSON && xhr.responseJSON.message) {
                    message = xhr.responseJSON.message;
                }
                showAlert('danger', message);
            },
            complete: function() {
                // Restore button state
                submitBtn.html(originalText);
                submitBtn.prop('disabled', false);
            }
        });
    });

    // Show alert messages
    function showAlert(type, message) {
        var alertHtml = '<div class="alert alert-' + type + ' alert-dismissible fade show" role="alert">' +
                       message +
                       '<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>' +
                       '</div>';
        
        $('.main-content .container-fluid').prepend(alertHtml);
        
        // Auto-hide after 5 seconds
        setTimeout(function() {
            $('.alert').fadeOut('slow');
        }, 5000);
    }

    // Data tables enhancement
    if ($.fn.DataTable) {
        $('.data-table').DataTable({
            responsive: true,
            pageLength: 25,
            order: [[0, 'desc']],
            language: {
                search: "Search:",
                lengthMenu: "Show _MENU_ entries",
                info: "Showing _START_ to _END_ of _TOTAL_ entries",
                paginate: {
                    first: "First",
                    last: "Last",
                    next: "Next",
                    previous: "Previous"
                }
            }
        });
    }

    // Chart.js default configuration
    if (typeof Chart !== 'undefined') {
        Chart.defaults.font.family = "'Inter', sans-serif";
        Chart.defaults.color = '#6c757d';
        Chart.defaults.borderColor = '#dee2e6';
    }

    // Sidebar state management
    var sidebar = document.getElementById('sidebar');
    if (sidebar) {
        // Remember sidebar state on desktop
        if (window.innerWidth >= 992) {
            var sidebarState = localStorage.getItem('sidebarState');
            if (sidebarState === 'hidden') {
                sidebar.classList.remove('show');
            } else {
                sidebar.classList.add('show');
            }
        }

        // Save sidebar state
        sidebar.addEventListener('hidden.bs.offcanvas', function() {
            if (window.innerWidth >= 992) {
                localStorage.setItem('sidebarState', 'hidden');
            }
        });

        sidebar.addEventListener('shown.bs.offcanvas', function() {
            if (window.innerWidth >= 992) {
                localStorage.setItem('sidebarState', 'shown');
            }
        });
    }
});

// Utility functions and enhanced modules
window.AdminPanel = {
    // Show loading overlay
    showLoading: function() {
        $('body').addClass('loading');
    },

    // Hide loading overlay
    hideLoading: function() {
        $('body').removeClass('loading');
    },

    // Format currency
    formatCurrency: function(amount) {
        return new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: 'INR'
        }).format(amount);
    },

    // Format date
    formatDate: function(date) {
        return new Intl.DateTimeFormat('en-IN', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        }).format(new Date(date));
    },

    // Confirm action
    confirm: function(message, callback) {
        if (confirm(message)) {
            callback();
        }
    },

    // Enhanced Search Module
    Search: {
        init: function() {
            this.initAutoComplete();
            this.initLiveSearch();
            this.initAdvancedFilters();
        },

        initAutoComplete: function() {
            // Service autocomplete
            $('.service-autocomplete').each(function() {
                var input = $(this);
                var resultsContainer = input.siblings('.autocomplete-results');
                var searchTimeout;

                input.on('input', function() {
                    clearTimeout(searchTimeout);
                    var query = $(this).val().trim();
                    
                    if (query.length < 2) {
                        resultsContainer.hide();
                        return;
                    }

                    searchTimeout = setTimeout(function() {
                        AdminPanel.Search.searchServices(query, function(results) {
                            AdminPanel.Search.displayAutocompleteResults(resultsContainer, results, 'service');
                        });
                    }, 300);
                });

                // Hide results when clicking outside
                $(document).on('click', function(e) {
                    if (!input.is(e.target) && !resultsContainer.is(e.target) && resultsContainer.has(e.target).length === 0) {
                        resultsContainer.hide();
                    }
                });
            });

            // Category autocomplete
            $('.category-autocomplete').each(function() {
                var input = $(this);
                var resultsContainer = input.siblings('.autocomplete-results');
                var searchTimeout;

                input.on('input', function() {
                    clearTimeout(searchTimeout);
                    var query = $(this).val().trim();
                    
                    if (query.length < 2) {
                        resultsContainer.hide();
                        return;
                    }

                    searchTimeout = setTimeout(function() {
                        AdminPanel.Search.searchCategories(query, function(results) {
                            AdminPanel.Search.displayAutocompleteResults(resultsContainer, results, 'category');
                        });
                    }, 300);
                });
            });

            // Employee autocomplete
            $('.employee-autocomplete').each(function() {
                var input = $(this);
                var resultsContainer = input.siblings('.autocomplete-results');
                var searchTimeout;

                input.on('input', function() {
                    clearTimeout(searchTimeout);
                    var query = $(this).val().trim();
                    
                    if (query.length < 2) {
                        resultsContainer.hide();
                        return;
                    }

                    searchTimeout = setTimeout(function() {
                        AdminPanel.Search.searchEmployees(query, function(results) {
                            AdminPanel.Search.displayAutocompleteResults(resultsContainer, results, 'employee');
                        });
                    }, 300);
                });
            });
        },

        initLiveSearch: function() {
            $('.live-search').on('input', function() {
                var input = $(this);
                var searchType = input.data('search-type');
                var query = input.val().trim();
                var resultsContainer = input.data('results-container');
                
                if (query.length < 2) {
                    $(resultsContainer).empty();
                    return;
                }

                AdminPanel.Search.performLiveSearch(searchType, query, resultsContainer);
            });
        },

        initAdvancedFilters: function() {
            $('.advanced-filter').on('change', function() {
                AdminPanel.Search.applyFilters();
            });

            $('#clearFilters').on('click', function() {
                $('.advanced-filter').val('');
                AdminPanel.Search.applyFilters();
            });
        },

        searchServices: function(query, callback) {
            $.ajax({
                url: '/admin-panel/ajax/services/search/',
                method: 'GET',
                data: { q: query, limit: 10 },
                success: function(response) {
                    if (response.success) {
                        callback(response.services);
                    }
                },
                error: function() {
                    callback([]);
                }
            });
        },

        searchCategories: function(query, callback) {
            $.ajax({
                url: '/admin-panel/ajax/categories/search/',
                method: 'GET',
                data: { q: query, limit: 10 },
                success: function(response) {
                    if (response.success) {
                        callback(response.categories);
                    }
                },
                error: function() {
                    callback([]);
                }
            });
        },

        searchEmployees: function(query, callback) {
            $.ajax({
                url: '/admin-panel/ajax/employees/search/',
                method: 'GET',
                data: { q: query, limit: 10 },
                success: function(response) {
                    if (response.success) {
                        callback(response.employees);
                    }
                },
                error: function() {
                    callback([]);
                }
            });
        },

        displayAutocompleteResults: function(container, results, type) {
            container.empty();
            
            if (results.length === 0) {
                container.append('<div class="autocomplete-item text-muted">No results found</div>');
            } else {
                results.forEach(function(item) {
                    var html = AdminPanel.Search.formatAutocompleteItem(item, type);
                    var element = $(html);
                    
                    element.on('click', function() {
                        AdminPanel.Search.selectAutocompleteItem(item, type, container);
                    });
                    
                    container.append(element);
                });
            }
            
            container.show();
        },

        formatAutocompleteItem: function(item, type) {
            switch (type) {
                case 'service':
                    return `<div class="autocomplete-item" data-id="${item.id}">
                        <strong>${item.name}</strong>
                        <small class="text-muted d-block">${item.category} - ${AdminPanel.formatCurrency(item.base_price)}</small>
                    </div>`;
                case 'category':
                    return `<div class="autocomplete-item" data-id="${item.id}">
                        <strong>${item.name}</strong>
                        <small class="text-muted d-block">${item.service_count} services</small>
                    </div>`;
                case 'employee':
                    return `<div class="autocomplete-item" data-id="${item.id}">
                        <strong>${item.name}</strong>
                        <small class="text-muted d-block">${item.specialization} - ${item.employee_id}</small>
                    </div>`;
                default:
                    return `<div class="autocomplete-item" data-id="${item.id}">${item.name}</div>`;
            }
        },

        selectAutocompleteItem: function(item, type, container) {
            var input = container.siblings('input');
            input.val(item.name);
            input.data('selected-id', item.id);
            container.hide();
            
            // Trigger custom event
            input.trigger('autocomplete:select', [item, type]);
        },

        performLiveSearch: function(searchType, query, resultsContainer) {
            var url = '/admin-panel/ajax/' + searchType + '/search/';
            
            $.ajax({
                url: url,
                method: 'GET',
                data: { q: query },
                success: function(response) {
                    if (response.success) {
                        AdminPanel.Search.displayLiveResults(response, resultsContainer, searchType);
                    }
                }
            });
        },

        displayLiveResults: function(response, container, type) {
            var results = response[type] || response.results || [];
            $(container).empty();
            
            if (results.length === 0) {
                $(container).append('<div class="text-muted p-3">No results found</div>');
            } else {
                results.forEach(function(item) {
                    var html = AdminPanel.Search.formatLiveResult(item, type);
                    $(container).append(html);
                });
            }
        },

        formatLiveResult: function(item, type) {
            // Format live search results based on type
            switch (type) {
                case 'services':
                    return `<div class="search-result-item p-2 border-bottom">
                        <h6 class="mb-1">${item.name}</h6>
                        <small class="text-muted">${item.category} - ${AdminPanel.formatCurrency(item.base_price)}</small>
                        <span class="badge ${item.is_active ? 'bg-success' : 'bg-secondary'} ms-2">
                            ${item.is_active ? 'Active' : 'Inactive'}
                        </span>
                    </div>`;
                default:
                    return `<div class="search-result-item p-2 border-bottom">${item.name}</div>`;
            }
        },

        applyFilters: function() {
            var filters = {};
            $('.advanced-filter').each(function() {
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
            
            window.location.href = currentUrl.toString();
        }
    },

    // Enhanced Forms Module
    Forms: {
        init: function() {
            this.initRealTimeValidation();
            this.initDynamicForms();
            this.initConfirmationDialogs();
        },

        initRealTimeValidation: function() {
            // Real-time validation for unique fields
            $('input[data-validate]').on('blur', function() {
                var input = $(this);
                var validateType = input.data('validate');
                var formType = input.closest('form').data('form-type');
                var excludeId = input.closest('form').data('exclude-id');
                
                AdminPanel.Forms.validateField(formType, validateType, input.val(), excludeId, function(result) {
                    AdminPanel.Forms.showValidationResult(input, result);
                });
            });
        },

        initDynamicForms: function() {
            // Dynamic form field updates
            $('.dynamic-form').on('change', 'select, input', function() {
                var form = $(this).closest('form');
                AdminPanel.Forms.updateDynamicFields(form);
            });

            // Add/remove dynamic fields
            $(document).on('click', '.add-field', function() {
                AdminPanel.Forms.addDynamicField($(this));
            });

            $(document).on('click', '.remove-field', function() {
                AdminPanel.Forms.removeDynamicField($(this));
            });
        },

        initConfirmationDialogs: function() {
            // Enhanced confirmation dialogs
            $('.confirm-action').on('click', function(e) {
                e.preventDefault();
                var button = $(this);
                var message = button.data('confirm-message') || 'Are you sure?';
                var title = button.data('confirm-title') || 'Confirm Action';
                
                AdminPanel.Forms.showConfirmDialog(title, message, function() {
                    if (button.is('a')) {
                        window.location.href = button.attr('href');
                    } else if (button.is('button[type="submit"]')) {
                        button.closest('form').submit();
                    }
                });
            });
        },

        validateField: function(formType, fieldName, fieldValue, excludeId, callback) {
            $.ajax({
                url: '/admin-panel/ajax/form/validate/',
                method: 'POST',
                data: {
                    form_type: formType,
                    field_name: fieldName,
                    field_value: fieldValue,
                    exclude_id: excludeId,
                    csrfmiddlewaretoken: $('[name=csrfmiddlewaretoken]').val()
                },
                success: function(response) {
                    callback(response);
                },
                error: function() {
                    callback({ valid: false, message: 'Validation error' });
                }
            });
        },

        showValidationResult: function(input, result) {
            var feedback = input.siblings('.validation-feedback');
            if (feedback.length === 0) {
                feedback = $('<div class="validation-feedback"></div>');
                input.after(feedback);
            }
            
            input.removeClass('is-valid is-invalid');
            
            if (result.valid) {
                input.addClass('is-valid');
                feedback.removeClass('invalid-feedback').addClass('valid-feedback');
                feedback.text(result.message);
            } else {
                input.addClass('is-invalid');
                feedback.removeClass('valid-feedback').addClass('invalid-feedback');
                feedback.text(result.message);
            }
            
            feedback.show();
        },

        updateDynamicFields: function(form) {
            // Update dependent fields based on form changes
            var formData = form.serialize();
            var updateUrl = form.data('update-url');
            
            if (updateUrl) {
                $.ajax({
                    url: updateUrl,
                    method: 'POST',
                    data: formData,
                    success: function(response) {
                        if (response.success && response.updates) {
                            AdminPanel.Forms.applyFieldUpdates(form, response.updates);
                        }
                    }
                });
            }
        },

        applyFieldUpdates: function(form, updates) {
            Object.keys(updates).forEach(function(fieldName) {
                var field = form.find('[name="' + fieldName + '"]');
                var update = updates[fieldName];
                
                if (update.type === 'options') {
                    AdminPanel.Forms.updateSelectOptions(field, update.options);
                } else if (update.type === 'value') {
                    field.val(update.value);
                } else if (update.type === 'visibility') {
                    field.closest('.form-group, .mb-3').toggle(update.visible);
                }
            });
        },

        updateSelectOptions: function(select, options) {
            var currentValue = select.val();
            select.empty();
            
            if (options.length === 0) {
                select.append('<option value="">No options available</option>');
            } else {
                options.forEach(function(option) {
                    var optionElement = $('<option></option>')
                        .attr('value', option.value)
                        .text(option.text);
                    
                    if (option.value === currentValue) {
                        optionElement.prop('selected', true);
                    }
                    
                    select.append(optionElement);
                });
            }
        },

        addDynamicField: function(button) {
            var template = button.data('template');
            var container = button.data('container');
            var templateHtml = $(template).html();
            
            $(container).append(templateHtml);
        },

        removeDynamicField: function(button) {
            var fieldGroup = button.closest('.dynamic-field-group');
            fieldGroup.remove();
        },

        showConfirmDialog: function(title, message, callback) {
            var modal = $('#confirmModal');
            if (modal.length === 0) {
                // Create modal if it doesn't exist
                modal = $(`
                    <div class="modal fade" id="confirmModal" tabindex="-1">
                        <div class="modal-dialog">
                            <div class="modal-content">
                                <div class="modal-header">
                                    <h5 class="modal-title"></h5>
                                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                                </div>
                                <div class="modal-body"></div>
                                <div class="modal-footer">
                                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                                    <button type="button" class="btn btn-danger" id="confirmAction">Confirm</button>
                                </div>
                            </div>
                        </div>
                    </div>
                `);
                $('body').append(modal);
            }
            
            modal.find('.modal-title').text(title);
            modal.find('.modal-body').text(message);
            
            modal.find('#confirmAction').off('click').on('click', function() {
                modal.modal('hide');
                callback();
            });
            
            modal.modal('show');
        }
    },

    // Enhanced Dashboard Module
    Dashboard: {
        charts: {},
        refreshInterval: null,

        init: function() {
            this.initCharts();
            this.initRealTimeUpdates();
            this.initQuickActions();
        },

        initCharts: function() {
            // Initialize appointment trend chart
            var appointmentCtx = document.getElementById('appointmentTrendChart');
            if (appointmentCtx) {
                this.loadChartData('appointments', function(data) {
                    AdminPanel.Dashboard.charts.appointments = new Chart(appointmentCtx, {
                        type: 'line',
                        data: data.chart_data,
                        options: AdminPanel.Dashboard.getChartOptions('line')
                    });
                });
            }

            // Initialize revenue chart
            var revenueCtx = document.getElementById('revenueChart');
            if (revenueCtx) {
                this.loadChartData('revenue', function(data) {
                    AdminPanel.Dashboard.charts.revenue = new Chart(revenueCtx, {
                        type: 'line',
                        data: data.chart_data,
                        options: AdminPanel.Dashboard.getChartOptions('line')
                    });
                });
            }

            // Initialize service popularity chart
            var serviceCtx = document.getElementById('servicePopularityChart');
            if (serviceCtx) {
                this.loadChartData('services', function(data) {
                    AdminPanel.Dashboard.charts.services = new Chart(serviceCtx, {
                        type: 'doughnut',
                        data: data.chart_data,
                        options: AdminPanel.Dashboard.getChartOptions('doughnut')
                    });
                });
            }

            // Initialize employee workload chart
            var employeeCtx = document.getElementById('employeeWorkloadChart');
            if (employeeCtx) {
                this.loadChartData('employees', function(data) {
                    AdminPanel.Dashboard.charts.employees = new Chart(employeeCtx, {
                        type: 'bar',
                        data: data.chart_data,
                        options: AdminPanel.Dashboard.getChartOptions('bar')
                    });
                });
            }
        },

        initRealTimeUpdates: function() {
            // Auto-refresh dashboard stats every 5 minutes
            this.refreshInterval = setInterval(function() {
                AdminPanel.Dashboard.refreshStats();
            }, 300000);

            // Manual refresh button
            $('#refreshDashboard').on('click', function() {
                AdminPanel.Dashboard.refreshStats();
                AdminPanel.Dashboard.refreshCharts();
            });
        },

        initQuickActions: function() {
            // Quick action buttons
            $('.quick-action').on('click', function() {
                var action = $(this).data('action');
                AdminPanel.Dashboard.performQuickAction(action);
            });
        },

        loadChartData: function(chartType, callback) {
            $.ajax({
                url: '/admin-panel/ajax/dashboard/charts/',
                method: 'GET',
                data: { type: chartType },
                success: function(response) {
                    if (response.success) {
                        callback(response);
                    }
                },
                error: function() {
                    console.error('Failed to load chart data for:', chartType);
                }
            });
        },

        getChartOptions: function(type) {
            var baseOptions = {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            };

            switch (type) {
                case 'line':
                    return $.extend(true, {}, baseOptions, {
                        scales: {
                            y: {
                                beginAtZero: true
                            }
                        }
                    });
                case 'bar':
                    return $.extend(true, {}, baseOptions, {
                        scales: {
                            y: {
                                beginAtZero: true
                            }
                        }
                    });
                case 'doughnut':
                    return baseOptions;
                default:
                    return baseOptions;
            }
        },

        refreshStats: function() {
            $.ajax({
                url: '/admin-panel/ajax/dashboard/quick-stats/',
                method: 'GET',
                success: function(response) {
                    if (response.success) {
                        AdminPanel.Dashboard.updateStatsDisplay(response.stats);
                    }
                }
            });
        },

        refreshCharts: function() {
            Object.keys(this.charts).forEach(function(chartKey) {
                var chart = AdminPanel.Dashboard.charts[chartKey];
                AdminPanel.Dashboard.loadChartData(chartKey, function(data) {
                    chart.data = data.chart_data;
                    chart.update();
                });
            });
        },

        updateStatsDisplay: function(stats) {
            // Update stat cards
            $('#todayAppointments').text(stats.today_appointments);
            $('#pendingAppointments').text(stats.pending_appointments);
            $('#monthAppointments').text(stats.month_appointments);
            $('#monthRevenue').text(AdminPanel.formatCurrency(stats.month_revenue));
            $('#activeServices').text(stats.active_services);
            $('#activeEmployees').text(stats.active_employees);
            $('#activeCategories').text(stats.active_categories);
            
            // Update last updated timestamp
            $('#lastUpdated').text('Last updated: ' + AdminPanel.formatDate(stats.last_updated));
        },

        performQuickAction: function(action) {
            switch (action) {
                case 'refresh':
                    this.refreshStats();
                    this.refreshCharts();
                    break;
                case 'export':
                    this.exportDashboardData();
                    break;
                default:
                    console.log('Unknown quick action:', action);
            }
        },

        exportDashboardData: function() {
            // Implement dashboard data export
            window.open('/admin-panel/dashboard/export/', '_blank');
        }
    },

    // Enhanced Notifications Module
    Notifications: {
        init: function() {
            this.loadNotifications();
            this.initNotificationPolling();
            this.initNotificationActions();
        },

        loadNotifications: function() {
            $.ajax({
                url: '/admin-panel/ajax/notifications/',
                method: 'GET',
                success: function(response) {
                    if (response.success) {
                        AdminPanel.Notifications.displayNotifications(response.notifications);
                        AdminPanel.Notifications.updateNotificationBadge(response.unread_count);
                    }
                }
            });
        },

        initNotificationPolling: function() {
            // Poll for new notifications every 2 minutes
            setInterval(function() {
                AdminPanel.Notifications.loadNotifications();
            }, 120000);
        },

        initNotificationActions: function() {
            // Mark notification as read
            $(document).on('click', '.notification-item', function() {
                var notification = $(this);
                notification.addClass('read');
                
                // Navigate to notification URL if available
                var url = notification.data('url');
                if (url) {
                    window.location.href = url;
                }
            });

            // Clear all notifications
            $('#clearNotifications').on('click', function() {
                AdminPanel.Notifications.clearAllNotifications();
            });
        },

        displayNotifications: function(notifications) {
            var container = $('#notificationsList');
            container.empty();
            
            if (notifications.length === 0) {
                container.append('<div class="text-muted p-3">No new notifications</div>');
            } else {
                notifications.forEach(function(notification) {
                    var html = AdminPanel.Notifications.formatNotification(notification);
                    container.append(html);
                });
            }
        },

        formatNotification: function(notification) {
            var typeIcon = AdminPanel.Notifications.getNotificationIcon(notification.type);
            var timeAgo = AdminPanel.Notifications.getTimeAgo(notification.timestamp);
            
            return `
                <div class="notification-item p-3 border-bottom" data-url="${notification.url || ''}">
                    <div class="d-flex">
                        <div class="notification-icon me-3">
                            <i class="${typeIcon}"></i>
                        </div>
                        <div class="notification-content flex-grow-1">
                            <h6 class="mb-1">${notification.title}</h6>
                            <p class="mb-1 text-muted">${notification.message}</p>
                            <small class="text-muted">${timeAgo}</small>
                        </div>
                    </div>
                </div>
            `;
        },

        getNotificationIcon: function(type) {
            switch (type) {
                case 'new_appointment':
                    return 'fas fa-calendar-plus text-success';
                case 'cancellation':
                    return 'fas fa-calendar-times text-danger';
                case 'assignment':
                    return 'fas fa-user-check text-info';
                default:
                    return 'fas fa-bell text-primary';
            }
        },

        getTimeAgo: function(timestamp) {
            var now = new Date();
            var time = new Date(timestamp);
            var diff = Math.floor((now - time) / 1000);
            
            if (diff < 60) return 'Just now';
            if (diff < 3600) return Math.floor(diff / 60) + ' minutes ago';
            if (diff < 86400) return Math.floor(diff / 3600) + ' hours ago';
            return Math.floor(diff / 86400) + ' days ago';
        },

        updateNotificationBadge: function(count) {
            var badge = $('#notificationBadge');
            if (count > 0) {
                badge.text(count).show();
            } else {
                badge.hide();
            }
        },

        clearAllNotifications: function() {
            $('#notificationsList').empty().append('<div class="text-muted p-3">No new notifications</div>');
            this.updateNotificationBadge(0);
        }
    }
};