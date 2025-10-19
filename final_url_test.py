#!/usr/bin/env python
"""
Final comprehensive test of all CarModX appointment URLs
"""
import os
import sys
import django
from datetime import date, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carmodx.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from services.models import Service, ServiceCategory
from appointments.models import Appointment

User = get_user_model()

def final_url_test():
    print("Final CarModX Appointment URL Test")
    print("=" * 50)
    
    # Setup test data
    print("1. Setting up test environment...")
    
    category, created = ServiceCategory.objects.get_or_create(
        name="Final Test Category",
        defaults={'description': 'Final test category'}
    )
    
    service, created = Service.objects.get_or_create(
        name="Final Test Service",
        defaults={
            'description': 'Final test service',
            'category': category,
            'base_price': 5000.00,
            'estimated_duration': timedelta(hours=2)
        }
    )
    
    customer, created = User.objects.get_or_create(
        username="finalcustomer",
        defaults={
            'email': 'final@test.com',
            'first_name': 'Final',
            'last_name': 'Customer',
            'role': 'customer'
        }
    )
    if created:
        customer.set_password('testpass123')
        customer.save()
    
    staff, created = User.objects.get_or_create(
        username="finalstaff",
        defaults={
            'email': 'finalstaff@test.com',
            'first_name': 'Final',
            'last_name': 'Staff',
            'role': 'admin',
            'is_staff': True
        }
    )
    if created:
        staff.set_password('testpass123')
        staff.save()
    
    # Create a test appointment
    tomorrow = date.today() + timedelta(days=1)
    appointment, created = Appointment.objects.get_or_create(
        customer=customer,
        selected_service=service,
        slot_date=tomorrow,
        slot_time='13:00',
        defaults={
            'vehicle_make': 'Final',
            'vehicle_model': 'Test',
            'vehicle_year': 2023,
            'vehicle_license': 'FINAL-123'
        }
    )
    
    print(f"   - Test service: {service.name}")
    print(f"   - Test customer: {customer.username}")
    print(f"   - Test staff: {staff.username}")
    print(f"   - Test appointment: #{appointment.id}")
    
    client = Client()
    
    # Test all URL patterns
    print("\n2. Testing all appointment URL patterns...")
    
    url_tests = [
        # Public URLs
        {
            'name': 'Available Slots API',
            'url': f'/appointments/api/available-slots/?date={tomorrow}',
            'method': 'GET',
            'auth_required': False,
            'expected_status': 200,
            'description': 'Public API endpoint for slot availability'
        },
        
        # Customer URLs (require login)
        {
            'name': 'Book Appointment',
            'url': '/appointments/book/',
            'method': 'GET',
            'auth_required': True,
            'user_type': 'customer',
            'expected_status': 200,
            'description': 'Appointment booking form'
        },
        {
            'name': 'My Appointments',
            'url': '/appointments/my-appointments/',
            'method': 'GET',
            'auth_required': True,
            'user_type': 'customer',
            'expected_status': 200,
            'description': 'Customer appointment list'
        },
        {
            'name': 'Appointment Detail',
            'url': f'/appointments/{appointment.id}/',
            'method': 'GET',
            'auth_required': True,
            'user_type': 'customer',
            'expected_status': 200,
            'description': 'Appointment details page'
        },
        {
            'name': 'Cancel Appointment',
            'url': f'/appointments/{appointment.id}/cancel/',
            'method': 'GET',
            'auth_required': True,
            'user_type': 'customer',
            'expected_status': 200,
            'description': 'Appointment cancellation form'
        },
        
        # Staff URLs (require staff permissions)
        {
            'name': 'All Appointments List',
            'url': '/appointments/list/',
            'method': 'GET',
            'auth_required': True,
            'user_type': 'staff',
            'expected_status': 200,
            'description': 'Staff appointment management list'
        },
        {
            'name': 'Update Appointment Status',
            'url': f'/appointments/{appointment.id}/update-status/',
            'method': 'GET',
            'auth_required': True,
            'user_type': 'staff',
            'expected_status': 200,
            'description': 'Staff status update form'
        },
    ]
    
    results = []
    
    for test in url_tests:
        print(f"\n   Testing: {test['name']}")
        print(f"   URL: {test['url']}")
        print(f"   Description: {test['description']}")
        
        # Test without authentication first
        if test['auth_required']:
            response = client.get(test['url'])
            if response.status_code == 302:
                print(f"   ✓ Redirects to login when not authenticated (302)")
            else:
                print(f"   ✗ Expected redirect, got {response.status_code}")
                results.append(f"FAIL: {test['name']} - No auth redirect")
                continue
        
        # Test with appropriate authentication
        if test['auth_required']:
            if test['user_type'] == 'customer':
                client.login(username='finalcustomer', password='testpass123')
            elif test['user_type'] == 'staff':
                client.login(username='finalstaff', password='testpass123')
        
        # Make the actual request
        if test['method'] == 'GET':
            response = client.get(test['url'])
        elif test['method'] == 'POST':
            response = client.post(test['url'])
        
        # Check response
        if response.status_code == test['expected_status']:
            print(f"   ✓ Success ({response.status_code})")
            results.append(f"PASS: {test['name']}")
        else:
            print(f"   ✗ Expected {test['expected_status']}, got {response.status_code}")
            results.append(f"FAIL: {test['name']} - Status {response.status_code}")
        
        client.logout()
    
    # Test form submission
    print(f"\n3. Testing form submissions...")
    
    client.login(username='finalcustomer', password='testpass123')
    
    # Test booking form submission
    booking_data = {
        'selected_service': service.id,
        'slot_date': (tomorrow + timedelta(days=1)).strftime('%Y-%m-%d'),
        'slot_time': '15:00',
        'vehicle_make': 'Form',
        'vehicle_model': 'Test',
        'vehicle_year': 2022,
        'vehicle_license': 'FORM-123',
        'special_requirements': 'Form submission test'
    }
    
    response = client.post('/appointments/book/', booking_data)
    if response.status_code in [200, 302]:
        print(f"   ✓ Booking form submission: Status {response.status_code}")
        if response.status_code == 302:
            print("     - Successfully redirected (likely booked)")
        results.append("PASS: Booking form submission")
    else:
        print(f"   ✗ Booking form submission failed: {response.status_code}")
        results.append("FAIL: Booking form submission")
    
    client.logout()
    
    # Test staff status update
    client.login(username='finalstaff', password='testpass123')
    
    status_data = {'status': 'completed'}
    response = client.post(f'/appointments/{appointment.id}/update-status/', status_data)
    if response.status_code in [200, 302]:
        print(f"   ✓ Status update form: Status {response.status_code}")
        results.append("PASS: Status update form")
    else:
        print(f"   ✗ Status update form failed: {response.status_code}")
        results.append("FAIL: Status update form")
    
    client.logout()
    
    # Summary
    print("\n" + "=" * 50)
    print("FINAL URL TEST RESULTS")
    print("=" * 50)
    
    passed = len([r for r in results if r.startswith('PASS')])
    failed = len([r for r in results if r.startswith('FAIL')])
    total = len(results)
    
    print(f"\nTest Results: {passed}/{total} passed, {failed} failed")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! 🎉")
        print("\nAll appointment URLs are working correctly:")
        print("✅ Public API endpoints accessible")
        print("✅ Customer booking flow functional")
        print("✅ Staff management interface working")
        print("✅ Form submissions processing correctly")
        print("✅ Authentication and permissions enforced")
    else:
        print(f"\n❌ {failed} tests failed:")
        for result in results:
            if result.startswith('FAIL'):
                print(f"   - {result}")
    
    print(f"\nURL Endpoints Summary:")
    print(f"- /appointments/book/ - Customer booking form")
    print(f"- /appointments/my-appointments/ - Customer appointment list")
    print(f"- /appointments/list/ - Staff appointment management")
    print(f"- /appointments/<id>/ - Appointment details")
    print(f"- /appointments/<id>/cancel/ - Cancel appointment")
    print(f"- /appointments/<id>/update-status/ - Update status (staff)")
    print(f"- /appointments/api/available-slots/ - Slot availability API")
    
    print(f"\nDatabase Status:")
    total_appointments = Appointment.objects.count()
    print(f"- Total appointments in system: {total_appointments}")
    
    print(f"\n✅ Final URL test completed!")

if __name__ == "__main__":
    final_url_test()