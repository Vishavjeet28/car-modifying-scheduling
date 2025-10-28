#!/usr/bin/env python3
"""
Debug the appointments list view directly
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append('/Users/vishavjeetsingh/untitled folder/untitled folder/car-modification-scheduling ')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carmodx.settings')
django.setup()

from django.contrib.auth import get_user_model
from appointments.models import Appointment
from appointments.views import appointment_list_view
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser

User = get_user_model()

# Create a request factory
factory = RequestFactory()

# Get the staff user
staff_user = User.objects.get(username='staffuser')

# Create a mock request
request = factory.get('/appointments/list/')
request.user = staff_user

print("Testing appointment_list_view directly...")
print(f"User: {request.user.username}")
print(f"Is staff: {request.user.is_staff}")
print(f"Role: {request.user.role}")

# Check appointments in database
appointments = Appointment.objects.all()
print(f"Total appointments: {appointments.count()}")

# Check if the view logic works
if not (request.user.is_staff or request.user.role == 'employee'):
    print("❌ User doesn't have permission")
else:
    print("✅ User has permission")
    
    # Get appointments queryset like the view does
    appointments = Appointment.objects.all().order_by('-slot_date', '-slot_time')
    print(f"Appointments after ordering: {appointments.count()}")
    
    for apt in appointments[:3]:
        print(f"- {apt.id}: {apt.customer.username} -> {apt.selected_service.name} on {apt.slot_date}")