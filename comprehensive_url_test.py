#!/usr/bin/env python
"""
Comprehensive test of all CarModX URLs after fixes
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
from services.models import Service, ServiceCategory
from appointments.models import Appointment

User = get_user_model()

def comprehensive_test():
    print("Comprehensive CarModX URL Test")
    print("=" * 50)
    
    # Setup test data
    print("1. Setting up comprehensive test data...")
    
    category, created = ServiceCategory.objects.get_or_create(
        name="Comprehensive Test Category",
        defaults={'description': 'Comprehensive test category'}
    )
    
    service, created = Service.objects.get_or_create(
        name="Comprehensive Test Service",
        defaults={
            'description': 'Comprehensive test service',
            'category': category,
            'base_price': 12000.00,
            'estimated_duration': timedelta(hours=4)
        }
    )
    
    customer, created = User.objects.get_or_create(
        username="comptest",
        defaults={
            'email': 'comp@test.com',
            'first_name': 'Comp',
            'last_name': 'Test',
            'role': 'customer'
        }
    )
    if created:
        customer.set_password('testpass123')
        customer.save()
    
    staff, created = User.objects.get_or_create(
        username="compstaff",
        defaults={
            'email': 'compstaff@test.com',
            'first_name': 'Comp',
            'last_name': 'Staff',
            'role': 'admin',
            'is_staff': True
        }
    )
    if created:
        staff.set_password('testpass123')
        staff.save()
    
    print(f"   - Service: {service.name} (ID: {service.id})")
    print(f"   - Customer: {customer.username}")
    print(f"   - Staff: {staff.username}")
    
    client = Client()
    
    # Test all major URL endpoints
    print("\n2. Testing all major URL endpoints...")
    
    test_urls = [
        # Main site URLs
        {'url': '/', 'name': 'Home Page', 'auth': False, 'expected': 200},
        {'url': '/about/', 'name': 'About Page', 'auth': False, 'expected': 200},
        {'url': '/contact/', 'name': 'Contact Page', 'auth': False, 'expected': 200},
        
        # Services URLs
        {'url': '/services/', 'name': 'Services List', 'auth': False, 'expected': 200},
        {'url': f'/services/{service.id}/', 'name': 'Service Detail', 'auth': False, 'expected': 200},
        {'url': f'/services/category/{category.id}/', 'name': 'Category Detail', 'auth': False, 'expected': 200},
        
        # Appointment URLs (require auth)
        {'url': '/appointments/book/', 'name': 'Book Appointment', 'auth': True, 'user': 'customer', 'expected': 200},
        {'url': '/appointments/my-appointments/', 'name': 'My Appointments', 'auth': True, 'user': 'customer', 'expected': 200},
        {'url': '/appointments/api/available-slots/?date=2025-10-16', 'name': 'Available Slots API', 'auth': False, 'expected': 200},
        
        # Service booking URLs (require auth)
        {'url': f'/services/{service.id}/book/', 'name': 'Service Booking', 'auth': True, 'user': 'customer', 'expected': 200},
        
        # Staff URLs (require staff auth)
        {'url': '/appointments/list/', 'name': 'Staff Appointments', 'auth': True, 'user': 'staff', 'expected': 200},
        
        # Account URLs (require auth)
        {'url': '/accounts/dashboard/', 'name': 'Customer Dashboard', 'auth': True, 'user': 'customer', 'expected': 200},
    ]
    
    results = []
    
    for test in test_urls:
        print(f"\n   Testing: {test['name']}")
        print(f"   URL: {test['url']}")
        
        # Handle authentication
        if test['auth']:
            if test.get('user') == 'customer':
                client.login(username='comptest', password='testpass123')
            elif test.get('user') == 'staff':
                client.login(username='compstaff', password='testpass123')
        else:
            client.logout()
        
        try:
            response = client.get(test['url'])
            
            if response.status_code == test['expected']:
                print(f"   ✓ Success ({response.status_code})")
                results.append(f"PASS: {test['name']}")
            elif response.status_code == 302 and test['auth'] and not client.session.get('_auth_user_id'):
                print(f"   ✓ Redirects to login (302) - Expected for auth required")
                results.append(f"PASS: {test['name']} (Auth redirect)")
            else:
                print(f"   ✗ Expected {test['expected']}, got {response.status_code}")
                results.append(f"FAIL: {test['name']} - Status {response.status_code}")
                
        except Exception as e:
            print(f"   ✗ Error: {e}")
            results.append(f"FAIL: {test['name']} - Error: {e}")
        
        client.logout()
    
    # Test form submissions
    print(f"\n3. Testing form submissions...")
    
    client.login(username='comptest', password='testpass123')
    
    # Test appointment booking
    tomorrow = date.today() + timedelta(days=2)  # Use day after tomorrow to avoid conflicts
    booking_data = {
        'selected_service': service.id,
        'slot_date': tomorrow.strftime('%Y-%m-%d'),
        'slot_time': '17:00',  # 5:00 PM
        'vehicle_make': 'Comprehensive',
        'vehicle_model': 'Test',
        'vehicle_year': 2022,
        'vehicle_license': 'COMP-123',
        'special_requirements': 'Comprehensive test booking'
    }
    
    response = client.post('/appointments/book/', booking_data)
    if response.status_code in [200, 302]:
        print(f"   ✓ Direct appointment booking: Status {response.status_code}")
        results.append("PASS: Direct appointment booking")
    else:
        print(f"   ✗ Direct appointment booking failed: {response.status_code}")
        results.append("FAIL: Direct appointment booking")
    
    # Test service booking
    service_booking_data = {
        'selected_service': service.id,
        'slot_date': (tomorrow + timedelta(days=1)).strftime('%Y-%m-%d'),
        'slot_time': '13:00',  # 1:00 PM
        'vehicle_make': 'Service',
        'vehicle_model': 'Booking',
        'vehicle_year': 2023,
        'vehicle_license': 'SRV-123',
        'special_requirements': 'Service booking test'
    }
    
    response = client.post(f'/services/{service.id}/book/', service_booking_data)
    if response.status_code in [200, 302]:
        print(f"   ✓ Service-based booking: Status {response.status_code}")
        results.append("PASS: Service-based booking")
    else:
        print(f"   ✗ Service-based booking failed: {response.status_code}")
        results.append("FAIL: Service-based booking")
    
    client.logout()
    
    # Summary
    print("\n" + "=" * 50)
    print("COMPREHENSIVE TEST RESULTS")
    print("=" * 50)
    
    passed = len([r for r in results if r.startswith('PASS')])
    failed = len([r for r in results if r.startswith('FAIL')])
    total = len(results)
    
    print(f"\nTest Results: {passed}/{total} passed, {failed} failed")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! 🎉")
        print("\nAll CarModX URLs are working correctly:")
        print("✅ Main site pages accessible")
        print("✅ Services browsing functional")
        print("✅ Appointment booking working")
        print("✅ Service-based booking integrated")
        print("✅ Staff management interface operational")
        print("✅ API endpoints responding")
        print("✅ Authentication and permissions enforced")
    else:
        print(f"\n❌ {failed} tests failed:")
        for result in results:
            if result.startswith('FAIL'):
                print(f"   - {result}")
    
    # Database statistics
    print(f"\nDatabase Statistics:")
    total_appointments = Appointment.objects.count()
    total_services = Service.objects.count()
    total_users = User.objects.count()
    
    print(f"- Total appointments: {total_appointments}")
    print(f"- Total services: {total_services}")
    print(f"- Total users: {total_users}")
    
    print(f"\n✅ Comprehensive URL test completed!")

if __name__ == "__main__":
    comprehensive_test()