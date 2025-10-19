#!/usr/bin/env python
"""
Test script to check all appointment URLs
"""
import os
import sys
import django
from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carmodx.settings')
django.setup()

from services.models import Service, ServiceCategory
from appointments.models import Appointment

User = get_user_model()

def test_urls():
    print("Testing CarModX Appointment URLs")
    print("=" * 50)
    
    client = Client()
    
    # Create test data
    print("1. Setting up test data...")
    
    # Create a service category and service
    category, created = ServiceCategory.objects.get_or_create(
        name="Test Category",
        defaults={'description': 'Test category'}
    )
    
    from datetime import timedelta
    
    service, created = Service.objects.get_or_create(
        name="Test Service",
        defaults={
            'description': 'Test service',
            'category': category,
            'base_price': 1000.00,
            'estimated_duration': timedelta(hours=2)
        }
    )
    
    # Create test users
    customer, created = User.objects.get_or_create(
        username="testcustomer",
        defaults={
            'email': 'customer@test.com',
            'role': 'customer',
            'password': 'testpass123'
        }
    )
    if created:
        customer.set_password('testpass123')
        customer.save()
    
    staff_user, created = User.objects.get_or_create(
        username="staffuser",
        defaults={
            'email': 'staff@test.com',
            'role': 'admin',
            'is_staff': True,
            'password': 'testpass123'
        }
    )
    if created:
        staff_user.set_password('testpass123')
        staff_user.save()
    
    # Create a test appointment
    appointment, created = Appointment.objects.get_or_create(
        customer=customer,
        selected_service=service,
        slot_date='2025-10-16',
        slot_time='09:00',
        defaults={
            'vehicle_make': 'Toyota',
            'vehicle_model': 'Camry',
            'vehicle_year': 2020,
            'vehicle_license': 'TEST-123'
        }
    )
    
    print(f"   - Created service: {service.name}")
    print(f"   - Created customer: {customer.username}")
    print(f"   - Created staff user: {staff_user.username}")
    print(f"   - Created appointment: #{appointment.id}")
    
    # Test URLs without authentication (should redirect to login)
    print("\n2. Testing URLs without authentication...")
    
    urls_requiring_auth = [
        ('book_appointment', 'appointments:book_appointment', {}),
        ('my_appointments', 'appointments:my_appointments', {}),
        ('appointment_detail', 'appointments:appointment_detail', {'appointment_id': appointment.id}),
        ('cancel_appointment', 'appointments:cancel_appointment', {'appointment_id': appointment.id}),
        ('appointment_list', 'appointments:appointment_list', {}),
        ('update_status', 'appointments:update_status', {'appointment_id': appointment.id}),
    ]
    
    for name, url_name, kwargs in urls_requiring_auth:
        try:
            url = reverse(url_name, kwargs=kwargs)
            response = client.get(url)
            if response.status_code == 302:
                print(f"   ✓ {name}: {url} -> Redirects to login (302)")
            else:
                print(f"   ✗ {name}: {url} -> Unexpected status {response.status_code}")
        except Exception as e:
            print(f"   ✗ {name}: Error - {e}")
    
    # Test API endpoint (should work without auth)
    print("\n3. Testing API endpoints...")
    
    try:
        url = reverse('appointments:available_slots_api')
        response = client.get(url + '?date=2025-10-16')
        if response.status_code == 200:
            print(f"   ✓ available_slots_api: {url} -> Success (200)")
            data = response.json()
            print(f"     - Returned {len(data.get('slots', []))} slots")
        else:
            print(f"   ✗ available_slots_api: {url} -> Status {response.status_code}")
    except Exception as e:
        print(f"   ✗ available_slots_api: Error - {e}")
    
    # Test URLs with customer authentication
    print("\n4. Testing URLs with customer authentication...")
    
    client.login(username='testcustomer', password='testpass123')
    
    customer_urls = [
        ('book_appointment', 'appointments:book_appointment', {}),
        ('my_appointments', 'appointments:my_appointments', {}),
        ('appointment_detail', 'appointments:appointment_detail', {'appointment_id': appointment.id}),
        ('cancel_appointment', 'appointments:cancel_appointment', {'appointment_id': appointment.id}),
    ]
    
    for name, url_name, kwargs in customer_urls:
        try:
            url = reverse(url_name, kwargs=kwargs)
            response = client.get(url)
            if response.status_code == 200:
                print(f"   ✓ {name}: {url} -> Success (200)")
            elif response.status_code == 302:
                print(f"   ~ {name}: {url} -> Redirect (302)")
            else:
                print(f"   ✗ {name}: {url} -> Status {response.status_code}")
        except Exception as e:
            print(f"   ✗ {name}: Error - {e}")
    
    client.logout()
    
    # Test URLs with staff authentication
    print("\n5. Testing URLs with staff authentication...")
    
    client.login(username='staffuser', password='testpass123')
    
    staff_urls = [
        ('appointment_list', 'appointments:appointment_list', {}),
        ('update_status', 'appointments:update_status', {'appointment_id': appointment.id}),
        ('appointment_detail', 'appointments:appointment_detail', {'appointment_id': appointment.id}),
    ]
    
    for name, url_name, kwargs in staff_urls:
        try:
            url = reverse(url_name, kwargs=kwargs)
            response = client.get(url)
            if response.status_code == 200:
                print(f"   ✓ {name}: {url} -> Success (200)")
            elif response.status_code == 302:
                print(f"   ~ {name}: {url} -> Redirect (302)")
            else:
                print(f"   ✗ {name}: {url} -> Status {response.status_code}")
        except Exception as e:
            print(f"   ✗ {name}: Error - {e}")
    
    client.logout()
    
    # Test form submissions
    print("\n6. Testing form submissions...")
    
    client.login(username='testcustomer', password='testpass123')
    
    # Test booking form submission
    try:
        url = reverse('appointments:book_appointment')
        form_data = {
            'selected_service': service.id,
            'slot_date': '2025-10-17',
            'slot_time': '11:00',
            'vehicle_make': 'Honda',
            'vehicle_model': 'Civic',
            'vehicle_year': 2021,
            'vehicle_license': 'FORM-123',
            'special_requirements': 'Test booking'
        }
        response = client.post(url, form_data)
        if response.status_code in [200, 302]:
            print(f"   ✓ Booking form submission -> Status {response.status_code}")
            if response.status_code == 302:
                print("     - Redirected (likely successful booking)")
        else:
            print(f"   ✗ Booking form submission -> Status {response.status_code}")
    except Exception as e:
        print(f"   ✗ Booking form submission: Error - {e}")
    
    client.logout()
    
    print("\n" + "=" * 50)
    print("URL Testing Summary")
    print("=" * 50)
    
    # List all appointment URLs
    print("\nAll Appointment URLs:")
    print("- /appointments/book/ (Book new appointment)")
    print("- /appointments/my-appointments/ (Customer's appointments)")
    print("- /appointments/list/ (All appointments - staff only)")
    print("- /appointments/<id>/ (Appointment details)")
    print("- /appointments/<id>/cancel/ (Cancel appointment)")
    print("- /appointments/<id>/update-status/ (Update status - staff only)")
    print("- /appointments/api/available-slots/ (API endpoint)")
    
    print("\n✓ URL testing completed!")

if __name__ == "__main__":
    test_urls()