#!/usr/bin/env python
"""
Test appointments list page for template field issues
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carmodx.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from appointments.models import Appointment

User = get_user_model()

def test_appointments_list_page():
    print("🔍 TESTING APPOINTMENTS LIST PAGE")
    print("=" * 50)
    
    client = Client()
    
    # Get an employee user (required for access)
    employee = User.objects.filter(role='employee').first()
    if not employee:
        print("❌ No employee users found")
        return
    
    print(f"✅ Testing with employee: {employee.username}")
    
    # Test without login (should redirect)
    response = client.get('/appointments/list/')
    print(f"📝 Without login: {response.status_code} (should be 302 redirect)")
    
    # Login as employee
    client.force_login(employee)
    
    # Test with login
    response = client.get('/appointments/list/')
    print(f"📝 With employee login: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Page loads successfully!")
        
        # Check appointments data
        appointments = Appointment.objects.all()
        print(f"📊 Total appointments in database: {appointments.count()}")
        
        # Check if page renders properly
        content = response.content.decode()
        
        # Check for template issues
        template_checks = [
            ('Page Title', 'Appointment Management' in content),
            ('Table Headers', 'Customer' in content and 'Service' in content),
            ('Search Form', 'Search & Filter' in content),
            ('Status Options', 'All Statuses' in content),
        ]
        
        print("\n🔍 Content Analysis:")
        for check_name, result in template_checks:
            status = "✅" if result else "❌"
            print(f"{status} {check_name}: {result}")
        
        # Check for error patterns
        error_patterns = [
            'VariableDoesNotExist',
            'AttributeError', 
            'TemplateSyntaxError',
            'RelatedObjectDoesNotExist'
        ]
        
        errors_found = []
        for pattern in error_patterns:
            if pattern in content:
                errors_found.append(pattern)
        
        if errors_found:
            print(f"\n❌ Template errors found: {errors_found}")
        else:
            print(f"\n✅ No obvious template errors in rendered content")
            
        # Test with admin
        admin = User.objects.filter(is_superuser=True).first()
        if admin:
            client.force_login(admin)
            response = client.get('/appointments/list/')
            print(f"📝 With admin login: {response.status_code}")
    
    else:
        print(f"❌ Page failed to load. Status: {response.status_code}")
        if hasattr(response, 'content'):
            print("Error content:", response.content.decode()[:500])

def check_appointment_fields():
    print("\n🔍 CHECKING APPOINTMENT MODEL FIELDS")
    print("=" * 50)
    
    appointment = Appointment.objects.first()
    if not appointment:
        print("❌ No appointments found in database")
        return
    
    print(f"✅ Testing with appointment #{appointment.id}")
    
    # Check field access
    field_tests = [
        ('selected_service.name', lambda: appointment.selected_service.name),
        ('selected_service.category.name', lambda: appointment.selected_service.category.name),
        ('selected_service.base_price', lambda: appointment.selected_service.base_price),
        ('slot_date', lambda: appointment.slot_date),
        ('get_slot_time_display', lambda: appointment.get_slot_time_display()),
        ('vehicle_make', lambda: appointment.vehicle_make),
        ('vehicle_model', lambda: appointment.vehicle_model),
        ('assigned_employee', lambda: appointment.assigned_employee),
        ('get_status_display', lambda: appointment.get_status_display()),
        ('get_priority_display', lambda: appointment.get_priority_display()),
    ]
    
    for field_name, field_access in field_tests:
        try:
            value = field_access()
            print(f"✅ {field_name}: {value}")
        except Exception as e:
            print(f"❌ {field_name}: {str(e)}")

if __name__ == "__main__":
    test_appointments_list_page()
    check_appointment_fields()