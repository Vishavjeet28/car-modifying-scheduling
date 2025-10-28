from django.contrib import admin
from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    """Appointment admin interface"""
    list_display = [
        'id', 'customer', 'selected_service', 'slot_date', 'slot_time', 
        'status', 'vehicle_info', 'created_at'
    ]
    list_filter = ['status', 'slot_date', 'slot_time', 'selected_service__category']
    search_fields = [
        'customer__username', 'customer__email', 'customer__first_name', 
        'customer__last_name', 'vehicle_make', 'vehicle_model', 'vehicle_license'
    ]
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'slot_date'
    ordering = ['-slot_date', '-slot_time']
    
    fieldsets = (
        ('Appointment Details', {
            'fields': ('customer', 'selected_service', 'slot_date', 'slot_time', 'status')
        }),
        ('Vehicle Information', {
            'fields': ('vehicle_make', 'vehicle_model', 'vehicle_year', 'vehicle_license')
        }),
        ('Additional Information', {
            'fields': ('special_requirements',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def vehicle_info(self, obj):
        return f"{obj.vehicle_year} {obj.vehicle_make} {obj.vehicle_model}"
    vehicle_info.short_description = 'Vehicle'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'customer', 'selected_service', 'selected_service__category'
        )