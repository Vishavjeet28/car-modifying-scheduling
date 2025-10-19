from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Extended User model with role-based access"""
    ROLE_CHOICES = [
        ('customer', 'Customer'),
        ('employee', 'Employee'),
        ('admin', 'Admin'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    phone_number = models.CharField(max_length=15, blank=True, help_text="Enter phone number in +91XXXXXXXXXX format")
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    def is_customer(self):
        return self.role == 'customer'
    
    def is_employee(self):
        return self.role == 'employee'
    
    def is_admin(self):
        return self.role == 'admin'


class Employee(models.Model):
    """Employee profile model"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_profile')
    employee_id = models.CharField(max_length=20, unique=True)
    specialization = models.CharField(max_length=100, blank=True)
    hire_date = models.DateField()
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.employee_id}"