#!/usr/bin/env python
"""
Simple script to check if all appointment URLs are properly configured
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carmodx.settings')
django.setup()

from django.urls import reverse, NoReverseMatch
from django.test import Client
from django.contrib.auth import get_user_model

User = get_user_model()

def check_url_patterns():
    print("Checking CarModX Appointment URL Patterns")
    print("=" * 50)
    
    # List of all appointment URLs to check
    url_patterns = [
        ('book_appointment', 'appointments:book_appointment', {}),
        ('my_appointments', 'appointments:my_appointments', {}),
        ('appointment_list', 'appointments:appointment_list', {}),
        ('appointment_detail', 'appointments:appointment_detail', {'appointment_id': 1}),
        ('cancel_appointment', 'appointments:cancel_appointment', {'appointment_id': 1}),
        ('update_status', 'appointments:update_status', {'appointment_id': 1}),
        ('available_slots_api', 'appointments:available_slots_api', {}),
    ]
    
    print("1. Checking URL pattern resolution...")
    
    for name, url_name, kwargs in url_patterns:
        try:
            url = reverse(url_name, kwargs=kwargs)
            print(f"   ✓ {name}: {url}")
        except NoReverseMatch as e:
            print(f"   ✗ {name}: URL pattern not found - {e}")
        except Exception as e:
            print(f"   ✗ {name}: Error - {e}")
    
    print("\n2. Testing URL accessibility with test client...")
    
    client = Client()
    
    # Test API endpoint (should work without auth)
    try:
        response = client.get('/appointments/api/available-slots/?date=2025-10-16')
        print(f"   ✓ API endpoint: Status {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"     - Returns {len(data.get('slots', []))} time slots")
    except Exception as e:
        print(f"   ✗ API endpoint: Error - {e}")
    
    # Test protected URLs (should redirect to login)
    protected_urls = [
        '/appointments/book/',
        '/appointments/my-appointments/',
        '/appointments/list/',
    ]
    
    for url in protected_urls:
        try:
            response = client.get(url)
            if response.status_code == 302:
                print(f"   ✓ {url}: Redirects to login (302)")
            elif response.status_code == 200:
                print(f"   ~ {url}: Accessible without auth (200)")
            else:
                print(f"   ? {url}: Status {response.status_code}")
        except Exception as e:
            print(f"   ✗ {url}: Error - {e}")
    
    print("\n3. Checking view imports...")
    
    try:
        from appointments import views
        view_functions = [
            'book_appointment_view',
            'my_appointments_view', 
            'appointment_list_view',
            'appointment_detail_view',
            'cancel_appointment_view',
            'update_appointment_status_view',
            'get_available_slots_api'
        ]
        
        for view_name in view_functions:
            if hasattr(views, view_name):
                print(f"   ✓ {view_name}: Found")
            else:
                print(f"   ✗ {view_name}: Not found")
                
    except Exception as e:
        print(f"   ✗ Error importing views: {e}")
    
    print("\n4. Checking template files...")
    
    import os
    template_files = [
        'appointments/templates/appointments/book_appointment.html',
        'appointments/templates/appointments/my_appointments.html',
        'appointments/templates/appointments/appointment_list.html',
        'appointments/templates/appointments/appointment_detail.html',
        'appointments/templates/appointments/cancel_appointment.html',
        'appointments/templates/appointments/update_status.html',
    ]
    
    for template_file in template_files:
        if os.path.exists(template_file):
            print(f"   ✓ {template_file}: Found")
        else:
            print(f"   ✗ {template_file}: Not found")
    
    print("\n5. Checking model and form imports...")
    
    try:
        from appointments.models import Appointment
        from appointments.forms import AppointmentBookingForm, AppointmentSearchForm
        print("   ✓ Models and forms import successfully")
        
        # Check model methods
        if hasattr(Appointment, 'get_available_slots'):
            print("   ✓ Appointment.get_available_slots method exists")
        else:
            print("   ✗ Appointment.get_available_slots method missing")
            
        if hasattr(Appointment, 'get_slot_capacity'):
            print("   ✓ Appointment.get_slot_capacity method exists")
        else:
            print("   ✗ Appointment.get_slot_capacity method missing")
            
    except Exception as e:
        print(f"   ✗ Error importing models/forms: {e}")
    
    print("\n" + "=" * 50)
    print("URL Check Summary")
    print("=" * 50)
    
    print("\nAppointment URLs:")
    print("- /appointments/book/ - Book new appointment")
    print("- /appointments/my-appointments/ - Customer appointments")
    print("- /appointments/list/ - All appointments (staff)")
    print("- /appointments/<id>/ - Appointment details")
    print("- /appointments/<id>/cancel/ - Cancel appointment")
    print("- /appointments/<id>/update-status/ - Update status")
    print("- /appointments/api/available-slots/ - API endpoint")
    
    print("\nAccess Requirements:")
    print("- Most URLs require login (@login_required)")
    print("- Staff URLs require is_staff permission")
    print("- API endpoint is public")
    
    print("\n✓ URL check completed!")

if __name__ == "__main__":
    check_url_patterns()