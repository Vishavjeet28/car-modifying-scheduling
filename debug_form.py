#!/usr/bin/env python
"""
Debug the booking form to see what validation errors are occurring
"""
import os
import sys
import django
from datetime import date, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carmodx.settings')
django.setup()

from django.contrib.auth import get_user_model
from services.models import Service, ServiceCategory
from appointments.forms import AppointmentBookingForm

User = get_user_model()

def debug_form():
    print("Debugging Appointment Booking Form")
    print("=" * 40)
    
    # Get or create test data
    category, created = ServiceCategory.objects.get_or_create(
        name="Test Category",
        defaults={'description': 'Test'}
    )
    
    service, created = Service.objects.get_or_create(
        name="Test Service",
        defaults={
            'description': 'Test service',
            'category': category,
            'base_price': 1000.00,
            'estimated_duration': timedelta(hours=2)
        }
    )
    
    customer, created = User.objects.get_or_create(
        username="debuguser",
        defaults={
            'email': 'debug@test.com',
            'role': 'customer'
        }
    )
    
    print(f"Service ID: {service.id}")
    print(f"Customer ID: {customer.id}")
    
    # Test form data
    tomorrow = date.today() + timedelta(days=1)
    
    form_data = {
        'selected_service': service.id,
        'slot_date': tomorrow.strftime('%Y-%m-%d'),
        'slot_time': '09:00',
        'vehicle_make': 'Honda',
        'vehicle_model': 'Civic',
        'vehicle_year': 2020,
        'vehicle_license': 'DEBUG-123',
        'special_requirements': 'Test booking'
    }
    
    print(f"\nForm data:")
    for key, value in form_data.items():
        print(f"  {key}: {value}")
    
    # Test form validation
    print(f"\nTesting form validation...")
    
    form = AppointmentBookingForm(data=form_data, user=customer)
    
    print(f"Form is valid: {form.is_valid()}")
    
    if not form.is_valid():
        print(f"\nForm errors:")
        for field, errors in form.errors.items():
            print(f"  {field}: {errors}")
        
        if form.non_field_errors():
            print(f"  Non-field errors: {form.non_field_errors()}")
    
    # Test individual field validation
    print(f"\nTesting individual fields...")
    
    # Test slot_date
    try:
        cleaned_date = form.fields['slot_date'].clean(tomorrow)
        print(f"  slot_date: ✓ {cleaned_date}")
    except Exception as e:
        print(f"  slot_date: ✗ {e}")
    
    # Test slot_time
    try:
        cleaned_time = form.fields['slot_time'].clean('09:00')
        print(f"  slot_time: ✓ {cleaned_time}")
    except Exception as e:
        print(f"  slot_time: ✗ {e}")
    
    # Test service
    try:
        cleaned_service = form.fields['selected_service'].clean(service.id)
        print(f"  selected_service: ✓ {cleaned_service}")
    except Exception as e:
        print(f"  selected_service: ✗ {e}")
    
    # Check if there are existing appointments that might cause conflicts
    from appointments.models import Appointment
    
    existing_appointments = Appointment.objects.filter(
        customer=customer,
        slot_date=tomorrow
    )
    
    print(f"\nExisting appointments for customer on {tomorrow}: {existing_appointments.count()}")
    
    slot_capacity = Appointment.get_slot_capacity(tomorrow, '09:00')
    print(f"Slot capacity for 9:00 AM on {tomorrow}: {slot_capacity}/5")
    
    print(f"\n✓ Form debugging completed!")

if __name__ == "__main__":
    debug_form()