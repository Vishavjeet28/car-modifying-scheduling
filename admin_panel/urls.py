from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    # Dashboard
    path('', views.AdminDashboardView.as_view(), name='dashboard'),
    path('dashboard/stats/', views.DashboardStatsAjaxView.as_view(), name='dashboard_stats_ajax'),
    
    # Admin Logs
    path('logs/', views.AdminLogListView.as_view(), name='logs'),
    
    # Service Management
    path('services/', views.ServiceListView.as_view(), name='service_list'),
    path('services/create/', views.ServiceCreateView.as_view(), name='service_create'),
    path('services/<int:pk>/edit/', views.ServiceUpdateView.as_view(), name='service_update'),
    path('services/<int:pk>/delete/', views.ServiceDeleteView.as_view(), name='service_delete'),
    path('services/bulk-action/', views.ServiceBulkActionView.as_view(), name='service_bulk_action'),
    path('services/<int:pk>/detail/', views.ServiceDetailAjaxView.as_view(), name='service_detail_ajax'),
    
    # Category Management
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/create/', views.CategoryCreateView.as_view(), name='category_create'),
    path('categories/<int:pk>/edit/', views.CategoryUpdateView.as_view(), name='category_update'),
    path('categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),
    path('categories/bulk-action/', views.CategoryBulkActionView.as_view(), name='category_bulk_action'),
    path('categories/<int:pk>/detail/', views.CategoryDetailAjaxView.as_view(), name='category_detail_ajax'),
    
    # Pricing Management
    path('pricing/', views.ServicePricingView.as_view(), name='pricing_matrix'),
    path('pricing/create/', views.PriceCreateView.as_view(), name='price_create'),
    path('pricing/<int:pk>/update/', views.PriceUpdateView.as_view(), name='price_update'),
    path('pricing/<int:pk>/delete/', views.PriceDeleteView.as_view(), name='price_delete'),
    path('pricing/conflict-check/', views.PricingConflictCheckView.as_view(), name='pricing_conflict_check'),
    path('pricing/service/<int:service_id>/prices/', views.ServicePricesAjaxView.as_view(), name='service_prices_ajax'),
    path('pricing/bulk-update/', views.BulkPricingUpdateView.as_view(), name='bulk_pricing_update'),
    
    # Employee Management
    path('employees/', views.EmployeeListView.as_view(), name='employee_list'),
    path('employees/create/', views.EmployeeCreateView.as_view(), name='employee_create'),
    path('employees/<int:pk>/edit/', views.EmployeeUpdateView.as_view(), name='employee_update'),
    path('employees/<int:pk>/detail/', views.EmployeeDetailView.as_view(), name='employee_detail'),
    path('employees/<int:pk>/toggle-status/', views.EmployeeActivationView.as_view(), name='employee_toggle_status'),
    path('employees/bulk-action/', views.EmployeeBulkActionView.as_view(), name='employee_bulk_action'),
    path('employees/<int:pk>/ajax-detail/', views.EmployeeDetailAjaxView.as_view(), name='employee_detail_ajax'),
    
    # System Settings Management
    path('settings/', views.SystemSettingsListView.as_view(), name='settings_list'),
    path('settings/create/', views.SystemSettingsCreateView.as_view(), name='settings_create'),
    path('settings/<int:pk>/edit/', views.SystemSettingsUpdateView.as_view(), name='settings_update'),
    path('settings/<int:pk>/delete/', views.SystemSettingsDeleteView.as_view(), name='settings_delete'),
    path('settings/bulk-action/', views.SystemSettingsBulkActionView.as_view(), name='settings_bulk_action'),
    path('settings/import/', views.SettingsImportView.as_view(), name='settings_import'),
    path('settings/reset/', views.SettingsResetView.as_view(), name='settings_reset'),
    
    # Settings Categories
    path('settings/time-slots/', views.TimeSlotSettingsView.as_view(), name='time_slot_settings'),
    path('settings/appointments/', views.AppointmentSettingsView.as_view(), name='appointment_settings'),
    path('settings/notifications/', views.NotificationSettingsView.as_view(), name='notification_settings'),
    
    # AJAX Endpoints for Enhanced Functionality
    path('ajax/services/search/', views.ServiceSearchAjaxView.as_view(), name='service_search_ajax'),
    path('ajax/categories/search/', views.CategorySearchAjaxView.as_view(), name='category_search_ajax'),
    path('ajax/employees/search/', views.EmployeeSearchAjaxView.as_view(), name='employee_search_ajax'),
    path('ajax/dashboard/charts/', views.DashboardChartsAjaxView.as_view(), name='dashboard_charts_ajax'),
    path('ajax/dashboard/quick-stats/', views.QuickStatsAjaxView.as_view(), name='quick_stats_ajax'),
    path('ajax/form/validate/', views.FormValidationAjaxView.as_view(), name='form_validation_ajax'),
    path('ajax/notifications/', views.NotificationAjaxView.as_view(), name='notifications_ajax'),
]