// Pricing Management JavaScript

$(document).ready(function() {
    AdminPanel.Pricing.init();
});

// Extend AdminPanel with Pricing module
AdminPanel.Pricing = {
    init: function() {
        this.initPricingMatrix();
        this.initPriceEditor();
        this.initBulkOperations();
        this.initConflictDetection();
    },

    initPricingMatrix: function() {
        // Service selection for pricing matrix
        $('#serviceSelect').on('change', function() {
            var serviceId = $(this).val();
            if (serviceId) {
                AdminPanel.Pricing.loadServicePrices(serviceId);
            } else {
                AdminPanel.Pricing.clearPricingMatrix();
            }
        });

        // Matrix cell editing
        $(document).on('click', '.price-cell[data-editable="true"]', function() {
            AdminPanel.Pricing.editPriceCell($(this));
        });

        // Matrix cell save/cancel
        $(document).on('click', '.save-price', function() {
            AdminPanel.Pricing.savePriceCell($(this));
        });

        $(document).on('click', '.cancel-price', function() {
            AdminPanel.Pricing.cancelPriceEdit($(this));
        });
    },

    initPriceEditor: function() {
        // Add new price form
        $('#addPriceForm').on('submit', function(e) {
            e.preventDefault();
            AdminPanel.Pricing.addNewPrice($(this));
        });

        // Price update form
        $('.price-update-form').on('submit', function(e) {
            e.preventDefault();
            AdminPanel.Pricing.updatePrice($(this));
        });

        // Price delete buttons
        $(document).on('click', '.delete-price', function() {
            AdminPanel.Pricing.deletePrice($(this));
        });
    },

    initBulkOperations: function() {
        // Bulk pricing operations
        $('#bulkPricingForm').on('submit', function(e) {
            e.preventDefault();
            AdminPanel.Pricing.performBulkOperation($(this));
        });

        // Percentage adjustment
        $('#applyPercentage').on('click', function() {
            AdminPanel.Pricing.applyPercentageChange();
        });
    },

    initConflictDetection: function() {
        // Real-time conflict detection
        $('#vehicleType, #complexityLevel').on('change', function() {
            AdminPanel.Pricing.checkPricingConflict();
        });
    },

    loadServicePrices: function(serviceId) {
        AdminPanel.showLoading();
        
        $.ajax({
            url: '/admin-panel/pricing/service/' + serviceId + '/prices/',
            method: 'GET',
            success: function(response) {
                if (response.success) {
                    AdminPanel.Pricing.displayPricingMatrix(response.service, response.prices);
                } else {
                    AdminPanel.Pricing.showError('Failed to load service prices');
                }
            },
            error: function() {
                AdminPanel.Pricing.showError('Error loading service prices');
            },
            complete: function() {
                AdminPanel.hideLoading();
            }
        });
    },

    displayPricingMatrix: function(service, prices) {
        var matrix = $('#pricingMatrix');
        matrix.empty();

        // Create matrix header
        var vehicleTypes = [...new Set(prices.map(p => p.vehicle_type))];
        var complexityLevels = [...new Set(prices.map(p => p.complexity_level))];

        if (vehicleTypes.length === 0 || complexityLevels.length === 0) {
            matrix.append('<div class="text-muted p-4">No pricing data available for this service</div>');
            return;
        }

        // Build matrix table
        var table = $('<table class="table table-bordered pricing-matrix-table"></table>');
        
        // Header row
        var headerRow = $('<tr><th>Vehicle Type / Complexity</th></tr>');
        complexityLevels.forEach(function(level) {
            headerRow.append('<th>' + level + '</th>');
        });
        table.append($('<thead></thead>').append(headerRow));

        // Data rows
        var tbody = $('<tbody></tbody>');
        vehicleTypes.forEach(function(vehicleType) {
            var row = $('<tr><td class="fw-bold">' + vehicleType + '</td></tr>');
            
            complexityLevels.forEach(function(complexityLevel) {
                var price = prices.find(p => 
                    p.vehicle_type === vehicleType && p.complexity_level === complexityLevel
                );
                
                var cell = $('<td class="price-cell" data-vehicle-type="' + vehicleType + 
                           '" data-complexity-level="' + complexityLevel + '"></td>');
                
                if (price) {
                    cell.attr('data-price-id', price.id)
                        .attr('data-editable', 'true')
                        .addClass(price.is_active ? 'price-active' : 'price-inactive')
                        .html('<span class="price-value">₹' + price.price + '</span>' +
                              '<span class="price-status ms-2">' + 
                              (price.is_active ? '<i class="fas fa-check-circle text-success"></i>' : 
                               '<i class="fas fa-times-circle text-danger"></i>') + '</span>');
                } else {
                    cell.addClass('price-empty')
                        .html('<button class="btn btn-sm btn-outline-primary add-price-btn">' +
                              '<i class="fas fa-plus"></i> Add Price</button>');
                }
                
                row.append(cell);
            });
            
            tbody.append(row);
        });
        
        table.append(tbody);
        matrix.append(table);

        // Show service info
        $('#selectedServiceInfo').html(
            '<h5>' + service.name + '</h5>' +
            '<p class="text-muted">Base Price: ₹' + service.base_price + '</p>'
        ).show();
    },

    editPriceCell: function(cell) {
        var priceId = cell.data('price-id');
        var currentPrice = cell.find('.price-value').text().replace('₹', '');
        
        var editForm = $(`
            <div class="price-edit-form">
                <input type="number" class="form-control form-control-sm price-input" 
                       value="${currentPrice}" step="0.01" min="0">
                <div class="mt-1">
                    <button class="btn btn-sm btn-success save-price" data-price-id="${priceId}">
                        <i class="fas fa-check"></i>
                    </button>
                    <button class="btn btn-sm btn-secondary cancel-price ms-1">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            </div>
        `);
        
        cell.html(editForm);
        cell.find('.price-input').focus().select();
    },

    savePriceCell: function(button) {
        var priceId = button.data('price-id');
        var cell = button.closest('.price-cell');
        var newPrice = cell.find('.price-input').val();
        
        if (!newPrice || parseFloat(newPrice) <= 0) {
            AdminPanel.Pricing.showError('Please enter a valid price');
            return;
        }

        AdminPanel.showLoading();
        
        $.ajax({
            url: '/admin-panel/pricing/' + priceId + '/update/',
            method: 'POST',
            data: {
                price: newPrice,
                vehicle_type: cell.data('vehicle-type'),
                complexity_level: cell.data('complexity-level'),
                is_active: true,
                csrfmiddlewaretoken: $('[name=csrfmiddlewaretoken]').val()
            },
            success: function(response) {
                if (response.success) {
                    AdminPanel.Pricing.refreshPriceCell(cell, response.price);
                    AdminPanel.Pricing.showSuccess(response.message);
                } else {
                    AdminPanel.Pricing.showError(response.error);
                }
            },
            error: function(xhr) {
                var message = xhr.responseJSON ? xhr.responseJSON.error : 'Error updating price';
                AdminPanel.Pricing.showError(message);
            },
            complete: function() {
                AdminPanel.hideLoading();
            }
        });
    },

    cancelPriceEdit: function(button) {
        var cell = button.closest('.price-cell');
        var priceId = cell.data('price-id');
        
        // Restore original content
        AdminPanel.Pricing.loadServicePrices($('#serviceSelect').val());
    },

    refreshPriceCell: function(cell, priceData) {
        cell.removeClass('price-empty')
            .addClass(priceData.is_active ? 'price-active' : 'price-inactive')
            .attr('data-price-id', priceData.id)
            .attr('data-editable', 'true')
            .html('<span class="price-value">₹' + priceData.price + '</span>' +
                  '<span class="price-status ms-2">' + 
                  (priceData.is_active ? '<i class="fas fa-check-circle text-success"></i>' : 
                   '<i class="fas fa-times-circle text-danger"></i>') + '</span>');
    },

    addNewPrice: function(form) {
        var formData = form.serialize();
        
        AdminPanel.showLoading();
        
        $.ajax({
            url: '/admin-panel/pricing/create/',
            method: 'POST',
            data: formData,
            success: function(response) {
                if (response.success) {
                    AdminPanel.Pricing.showSuccess(response.message);
                    form[0].reset();
                    // Refresh the pricing matrix
                    var serviceId = $('#serviceSelect').val();
                    if (serviceId) {
                        AdminPanel.Pricing.loadServicePrices(serviceId);
                    }
                } else {
                    AdminPanel.Pricing.showError(response.error);
                }
            },
            error: function(xhr) {
                var message = xhr.responseJSON ? xhr.responseJSON.error : 'Error creating price';
                AdminPanel.Pricing.showError(message);
            },
            complete: function() {
                AdminPanel.hideLoading();
            }
        });
    },

    deletePrice: function(button) {
        var priceId = button.data('price-id');
        var vehicleType = button.data('vehicle-type');
        var complexityLevel = button.data('complexity-level');
        
        AdminPanel.Forms.showConfirmDialog(
            'Delete Price',
            `Are you sure you want to delete the price for ${vehicleType} - ${complexityLevel}?`,
            function() {
                AdminPanel.showLoading();
                
                $.ajax({
                    url: '/admin-panel/pricing/' + priceId + '/delete/',
                    method: 'POST',
                    data: {
                        csrfmiddlewaretoken: $('[name=csrfmiddlewaretoken]').val()
                    },
                    success: function(response) {
                        if (response.success) {
                            AdminPanel.Pricing.showSuccess(response.message);
                            // Refresh the pricing matrix
                            var serviceId = $('#serviceSelect').val();
                            if (serviceId) {
                                AdminPanel.Pricing.loadServicePrices(serviceId);
                            }
                        } else {
                            AdminPanel.Pricing.showError(response.error);
                        }
                    },
                    error: function(xhr) {
                        var message = xhr.responseJSON ? xhr.responseJSON.error : 'Error deleting price';
                        AdminPanel.Pricing.showError(message);
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
        
        AdminPanel.showLoading();
        
        $.ajax({
            url: '/admin-panel/pricing/bulk-update/',
            method: 'POST',
            data: formData,
            success: function(response) {
                if (response.success) {
                    AdminPanel.Pricing.showSuccess(response.message);
                    // Refresh the pricing matrix
                    var serviceId = $('#serviceSelect').val();
                    if (serviceId) {
                        AdminPanel.Pricing.loadServicePrices(serviceId);
                    }
                } else {
                    AdminPanel.Pricing.showError(response.error);
                }
            },
            error: function(xhr) {
                var message = xhr.responseJSON ? xhr.responseJSON.error : 'Error performing bulk operation';
                AdminPanel.Pricing.showError(message);
            },
            complete: function() {
                AdminPanel.hideLoading();
            }
        });
    },

    applyPercentageChange: function() {
        var percentage = $('#percentageChange').val();
        var serviceId = $('#serviceSelect').val();
        
        if (!percentage || !serviceId) {
            AdminPanel.Pricing.showError('Please select a service and enter a percentage');
            return;
        }
        
        AdminPanel.Forms.showConfirmDialog(
            'Apply Percentage Change',
            `Are you sure you want to apply a ${percentage}% change to all prices for this service?`,
            function() {
                $.ajax({
                    url: '/admin-panel/pricing/bulk-update/',
                    method: 'POST',
                    data: {
                        action: 'apply_percentage',
                        service_id: serviceId,
                        percentage: percentage,
                        csrfmiddlewaretoken: $('[name=csrfmiddlewaretoken]').val()
                    },
                    success: function(response) {
                        if (response.success) {
                            AdminPanel.Pricing.showSuccess(response.message);
                            AdminPanel.Pricing.loadServicePrices(serviceId);
                            $('#percentageChange').val('');
                        } else {
                            AdminPanel.Pricing.showError(response.error);
                        }
                    },
                    error: function(xhr) {
                        var message = xhr.responseJSON ? xhr.responseJSON.error : 'Error applying percentage change';
                        AdminPanel.Pricing.showError(message);
                    }
                });
            }
        );
    },

    checkPricingConflict: function() {
        var serviceId = $('#serviceSelect').val();
        var vehicleType = $('#vehicleType').val();
        var complexityLevel = $('#complexityLevel').val();
        
        if (!serviceId || !vehicleType || !complexityLevel) {
            return;
        }
        
        $.ajax({
            url: '/admin-panel/pricing/conflict-check/',
            method: 'POST',
            data: {
                service_id: serviceId,
                vehicle_type: vehicleType,
                complexity_level: complexityLevel,
                csrfmiddlewaretoken: $('[name=csrfmiddlewaretoken]').val()
            },
            success: function(response) {
                if (response.conflict) {
                    AdminPanel.Pricing.showConflictWarning(response.message, response.existing_price);
                } else {
                    AdminPanel.Pricing.clearConflictWarning();
                }
            }
        });
    },

    showConflictWarning: function(message, existingPrice) {
        var warning = $('#conflictWarning');
        if (warning.length === 0) {
            warning = $('<div id="conflictWarning" class="alert alert-warning mt-2"></div>');
            $('#addPriceForm').prepend(warning);
        }
        
        warning.html(`
            <i class="fas fa-exclamation-triangle me-2"></i>
            ${message}
            <br><small>Existing price: ₹${existingPrice.price} (${existingPrice.is_active ? 'Active' : 'Inactive'})</small>
        `).show();
    },

    clearConflictWarning: function() {
        $('#conflictWarning').hide();
    },

    clearPricingMatrix: function() {
        $('#pricingMatrix').empty().append('<div class="text-muted p-4">Select a service to view pricing matrix</div>');
        $('#selectedServiceInfo').hide();
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