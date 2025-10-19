from django.db import models
from django.core.validators import MinValueValidator


class ServiceCategory(models.Model):
    """Service categories for organizing services"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Font Awesome icon class")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Service Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Service(models.Model):
    """Car modification services"""
    name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name='services')
    base_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    estimated_duration = models.DurationField(help_text="Estimated time to complete the service")
    is_active = models.BooleanField(default=True)
    image = models.ImageField(upload_to='services/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['category', 'name']
    
    def __str__(self):
        return f"{self.name} - ₹{self.base_price}"
    
    @property
    def duration_hours(self):
        """Return duration in hours for display"""
        total_seconds = self.estimated_duration.total_seconds()
        return total_seconds / 3600


class ServicePrice(models.Model):
    """Dynamic pricing for services based on vehicle type or complexity"""
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='prices')
    vehicle_type = models.CharField(max_length=50, blank=True, help_text="e.g., Sedan, SUV, Sports Car")
    complexity_level = models.CharField(max_length=20, blank=True, help_text="e.g., Basic, Standard, Premium")
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['service', 'vehicle_type', 'complexity_level']
    
    def __str__(self):
        return f"{self.service.name} - {self.vehicle_type} - ₹{self.price}"