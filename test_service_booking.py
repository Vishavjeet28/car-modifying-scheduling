#!/usr/bin/env python
"""
Test the service booking integration
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

def test_service_booking():
    print("Testing Service Booking Integration")
    print("=" * 40)
    
    # Setup test data
    print("1. Setting up test data...")
    
    category, created = ServiceCategory.objects.get_or_create(
        name="Service Test Category",
        defaults={'description': 'Service test category'}
    )
    
    service, created = Service.objects.get_or_create(
        name="Service Test Service",
        defaults={
            'description': 'Service test service',
            'category': category,
            'base_price': 8000.00,
            'estimated_duration': timedelta(hours=3)
        }
    )
    
    customer, created = User.objects.get_or_create(
        username="servicecustomer",
        defaults={
            'email': 'service@test.com',
            'first_name': 'Service',
            'last_name': 'Customer',
            'role': 'customer'
        }
    )
    if created:
        customer.set_password('testpass123')
        customer.save()
    
    print(f"   - Service: {service.name} (ID: {service.id})")
    print(f"   - Customer: {customer.username}")
    
    client = Client()
    
    # Test service booking page access
    print("\n2. Testing service booking page access...")
    
    # Without login
    response = client.get(f'/services/{service.id}/book/')
    if response.status_code == 302:
        print("   ✓ Redirects to login when not authenticated")
    else:
        print(f"   ✗ Expected redirect, got {response.status_code}")
        return
    
    # With login
    client.login(username='servicecustomer', password='testpass123')
    response = client.get(f'/services/{service.id}/book/')
    if response.status_code == 200:
        print("   ✓ Service booking page accessible")
        if b'Book Service' in response.content:
            print("   ✓ Booking form is present")
        else:
            print("   ✗ Booking form not found")
    else:
        print(f"   ✗ Service booking page failed: {response.status_code}")
        return
    
    # Test booking form submission
    print("\n3. Testing service booking form submission...")
    
    tomorrow = date.today() + timedelta(days=1)
    booking_data = {
        'selected_service': service.id,
        'slot_date': tomorrow.strftime('%Y-%m-%d'),
        'slot_time': '15:00',  # 3:00 PM
        'vehicle_make': 'Service',
        'vehicle_model': 'Test',
        'vehicle_year': 2021,
        'vehicle_license': 'SVC-123',
        'special_requirements': 'Service booking test'
    }
    
    response = client.post(f'/services/{service.id}/book/', booking_data)
    
    if response.status_code == 302:
        print("   ✓ Booking form submitted successfully (redirected)")
        
        # Check if appointment was created
        appointment = Appointment.objects.filter(
            customer=customer,
            selected_service=service,
            slot_date=tomorrow,
            slot_time='15:00'
        ).first()
        
        if appointment:
            print(f"   ✓ Appointment #{appointment.id} created successfully")
            print(f"     - Service: {appointment.selected_service.name}")
            print(f"     - Date: {appointment.slot_date}")
            print(f"     - Time: {appointment.get_slot_time_display()}")
            print(f"     - Status: {appointment.get_status_display()}")
        else:
            print("   ✗ Appointment not found in database")
            
    elif response.status_code == 200:
        print("   ~ Booking form returned (may have validation errors)")
        if b'error' in response.content.lower():
            print("   - Form contains errors")
        return
    else:
        print(f"   ✗ Booking form failed: {response.status_code}")
        return
    
    print("\n4. Testing service detail page integration...")
    
    # Test service detail page
    response = client.get(f'/services/{service.id}/')
    if response.status_code == 200:
        print("   ✓ Service detail page accessible")
        if f'/services/{service.id}/book/'.encode() in response.content:
            print("   ✓ Book service link is present")
        else:
            print("   ✗ Book service link not found")
    else:
        print(f"   ✗ Service detail page failed: {response.status_code}")
    
    print("\n" + "=" * 40)
    print("Service Booking Test Summary")
    print("=" * 40)
    
    total_appointments = Appointment.objects.filter(selected_service=service).count()
    print(f"\nAppointments for {service.name}: {total_appointments}")
    
    print(f"\nService Booking URLs:")
    print(f"- /services/{service.id}/ - Service details")
    print(f"- /services/{service.id}/book/ - Book appointment")
    
    print(f"\n✅ Service booking integration test completed!")

if __name__ == "__main__":
    test_service_booking()