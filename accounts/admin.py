from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Employee


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User admin interface"""
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff', 'date_joined')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('-date_joined',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role', 'phone_number', 'address')}),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('role', 'phone_number', 'address')}),
    )


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    """Employee admin interface"""
    list_display = ('user', 'employee_id', 'specialization', 'hire_date', 'is_active')
    list_filter = ('is_active', 'hire_date', 'specialization')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'employee_id')
    ordering = ('-hire_date',)
    
    fieldsets = (
        ('Employee Information', {
            'fields': ('user', 'employee_id', 'specialization', 'hire_date', 'is_active')
        }),
    )