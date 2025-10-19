#!/usr/bin/env python
"""
Final verification that appointment prices are displaying correctly
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

def final_price_verification():
    print("Final Price Display Verification")
    print("=" * 40)
    
    # Create a new appointment with a clear, distinct price
    category, created = ServiceCategory.objects.get_or_create(
        name="Final Price Test",
        defaults={'description': 'Final price test category'}
    )
    
    service, created = Service.objects.get_or_create(
        name="Final Price Test Service",
        defaults={
            'description': 'Service for final price verification',
            'category': category,
            'base_price': 25000.00,  # Clear price: ₹25,000
            'estimated_duration': timedelta(hours=3)
        }
    )
    
    customer, created = User.objects.get_or_create(
        username="finalpricetest",
        defaults={
            'email': 'finalprice@test.com',
            'role': 'customer'
        }
    )
    if created:
        customer.set_password('testpass123')
        customer.save()
    
    # Create a fresh appointment
    appointment = Appointment.objects.create(
        customer=customer,
        selected_service=service,
        slot_date=date.today() + timedelta(days=3),
        slot_time='15:00',
        vehicle_make='Final',
        vehicle_model='Price',
        vehicle_year=2024,
        vehicle_license='FINAL-789'
    )
    
    print(f"✅ Created appointment #{appointment.id}")
    print(f"   Service: {service.name}")
    print(f"   Price: ₹{service.base_price}")
    print(f"   Customer: {customer.username}")
    
    client = Client()
    client.login(username='finalpricetest', password='testpass123')
    
    # Test all relevant pages
    test_pages = [
        {
            'name': 'My Appointments',
            'url': '/appointments/my-appointments/',
            'should_contain_price': True
        },
        {
            'name': 'Appointment Detail',
            'url': f'/appointments/{appointment.id}/',
            'should_contain_price': True
        },
        {
            'name': 'Service Detail',
            'url': f'/services/{service.id}/',
            'should_contain_price': True
        }
    ]
    
    all_passed = True
    
    for test in test_pages:
        print(f"\n📋 Testing {test['name']}...")
        print(f"   URL: {test['url']}")
        
        response = client.get(test['url'])
        
        if response.status_code == 200:
            print("   ✅ Page loaded successfully")
            
            if test['should_contain_price']:
                price_variations = [
                    f"₹{service.base_price}",  # ₹25000.0
                    f"₹{service.base_price:.2f}",  # ₹25000.00
                    "₹25000",
                    "₹25,000",
                    "25000"
                ]
                
                price_found = False
                for price_text in price_variations:
                    if price_text.encode() in response.content:
                        print(f"   ✅ Price found: '{price_text}'")
                        price_found = True
                        break
                
                if not price_found:
                    print(f"   ❌ Price NOT found in any format")
                    all_passed = False
                
                # Check for service name
                if service.name.encode() in response.content:
                    print(f"   ✅ Service name found: '{service.name}'")
                else:
                    print(f"   ❌ Service name NOT found: '{service.name}'")
                    all_passed = False
            
        else:
            print(f"   ❌ Page failed to load: {response.status_code}")
            all_passed = False
    
    # Test booking flow
    print(f"\n📋 Testing booking flow...")
    
    # Test service booking page
    response = client.get(f'/services/{service.id}/book/')
    if response.status_code == 200:
        print("   ✅ Service booking page loaded")
        if f"₹{service.base_price}".encode() in response.content:
            print("   ✅ Price shown in booking page")
        else:
            print("   ❌ Price NOT shown in booking page")
            all_passed = False
    else:
        print(f"   ❌ Service booking page failed: {response.status_code}")
        all_passed = False
    
    print(f"\n" + "=" * 40)
    print("FINAL VERIFICATION RESULTS")
    print("=" * 40)
    
    if all_passed:
        print("\n🎉 ALL PRICE DISPLAYS ARE WORKING CORRECTLY! 🎉")
        print("\n✅ Price is visible in:")
        print("   - My Appointments page")
        print("   - Appointment Detail page")
        print("   - Service Detail page")
        print("   - Service Booking page")
        print("\n✅ Service information is complete")
        print("✅ Templates are rendering correctly")
        print("✅ Database relationships are working")
    else:
        print("\n❌ Some price displays are not working correctly")
        print("   Please check the failed tests above")
    
    print(f"\n📊 Test Summary:")
    print(f"   - Appointment ID: #{appointment.id}")
    print(f"   - Service: {service.name}")
    print(f"   - Price: ₹{service.base_price}")
    print(f"   - Customer: {customer.username}")
    
    print(f"\n✅ Final price verification completed!")

if __name__ == "__main__":
    final_price_verification()