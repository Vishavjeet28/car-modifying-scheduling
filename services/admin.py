from django.contrib import admin
from .models import ServiceCategory, Service, ServicePrice


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    """Service Category admin interface"""
    list_display = ('name', 'icon', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('name',)
    
    fieldsets = (
        ('Category Information', {
            'fields': ('name', 'description', 'icon', 'is_active')
        }),
    )


class ServicePriceInline(admin.TabularInline):
    """Inline admin for service prices"""
    model = ServicePrice
    extra = 1
    fields = ('vehicle_type', 'complexity_level', 'price', 'is_active')


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    """Service admin interface"""
    list_display = ('name', 'category', 'base_price', 'estimated_duration', 'is_active', 'created_at')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('name', 'description', 'category__name')
    ordering = ('category', 'name')
    inlines = [ServicePriceInline]
    
    fieldsets = (
        ('Service Information', {
            'fields': ('name', 'description', 'category', 'base_price', 'estimated_duration', 'is_active')
        }),
        ('Media', {
            'fields': ('image',)
        }),
    )


@admin.register(ServicePrice)
class ServicePriceAdmin(admin.ModelAdmin):
    """Service Price admin interface"""
    list_display = ('service', 'vehicle_type', 'complexity_level', 'price', 'is_active')
    list_filter = ('is_active', 'vehicle_type', 'complexity_level', 'service__category')
    search_fields = ('service__name', 'vehicle_type', 'complexity_level')
    ordering = ('service', 'vehicle_type', 'complexity_level')
    
    fieldsets = (
        ('Price Information', {
            'fields': ('service', 'vehicle_type', 'complexity_level', 'price', 'is_active')
        }),
    )