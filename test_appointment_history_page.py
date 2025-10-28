#!/usr/bin/env python
"""
Test script for appointment history page
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carmodx.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from appointments.models import Appointment

User = get_user_model()

def test_appointment_history_page():
    print("🔍 Testing Appointment History Page")
    print("=" * 50)
    
    client = Client()
    
    # Get a customer user
    customer = User.objects.filter(role='customer').first()
    if not customer:
        print("❌ No customer users found")
        return
    
    print(f"✅ Testing with customer: {customer.username}")
    
    # Test without login (should redirect)
    response = client.get('/accounts/appointment-history/')
    print(f"📝 Without login: {response.status_code} (should be 302 redirect)")
    
    # Login as customer
    client.force_login(customer)
    
    # Test with login
    response = client.get('/accounts/appointment-history/')
    print(f"📝 With customer login: {response.status_code} (should be 200)")
    
    if response.status_code == 200:
        print("✅ Page loads successfully!")
        
        # Check appointments data
        appointments = Appointment.objects.filter(customer=customer)
        print(f"📊 Total appointments for this customer: {appointments.count()}")
        
        # Check if page renders properly
        content = response.content.decode()
        if 'Appointment History' in content:
            print("✅ Page title found")
        if customer.appointments.exists():
            if 'card' in content and 'Appointment #' in content:
                print("✅ Appointment cards are being rendered")
            else:
                print("⚠️ Appointment cards may not be rendering properly")
        else:
            if 'No Appointments Found' in content:
                print("✅ Empty state message displayed correctly")
        
        # Test with different user types
        print("\n🔍 Testing with other user types:")
        
        # Test with employee
        employee = User.objects.filter(role='employee').first()
        if employee:
            client.force_login(employee)
            response = client.get('/accounts/appointment-history/')
            print(f"📝 With employee login: {response.status_code} (should redirect to dashboard)")
        
        # Test with admin
        admin = User.objects.filter(role='admin').first()
        if admin:
            client.force_login(admin)
            response = client.get('/accounts/appointment-history/')
            print(f"📝 With admin login: {response.status_code} (should redirect to dashboard)")
    
    else:
        print(f"❌ Page failed to load. Status: {response.status_code}")
        if hasattr(response, 'content'):
            print("Error content:", response.content.decode()[:500])

def check_template_fields():
    print("\n🔍 Checking Template Field Compatibility")
    print("=" * 50)
    
    # Get a sample appointment
    appointment = Appointment.objects.first()
    if not appointment:
        print("❌ No appointments found in database")
        return
    
    print(f"✅ Testing with appointment #{appointment.id}")
    
    # Check required fields exist
    required_fields = [
        'selected_service.name',
        'selected_service.description', 
        'selected_service.base_price',
        'slot_date',
        'get_slot_time_display',
        'vehicle_make',
        'vehicle_model',
        'assigned_employee',
        'get_status_display',
        'created_at'
    ]
    
    for field_path in required_fields:
        try:
            # Navigate through the field path
            obj = appointment
            for field in field_path.split('.'):
                if hasattr(obj, field):
                    obj = getattr(obj, field)
                    if callable(obj):
                        obj = obj()
                else:
                    raise AttributeError(f"No attribute '{field}'")
            print(f"✅ {field_path}: {obj}")
        except Exception as e:
            print(f"❌ {field_path}: {str(e)}")

if __name__ == "__main__":
    test_appointment_history_page()
    check_template_fields()