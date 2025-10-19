#!/usr/bin/env python3

"""
Test script for the new redesigned slot time selection interface
Tests the complete booking flow with the new visual slot selection
"""

import os
import sys
import django

# Setup Django environment
sys.path.append('/Users/vishavjeetsingh/untitled folder/untitled folder/detailcursor')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carmodx.settings')
django.setup()

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from services.models import Service, ServiceCategory
from appointments.models import Appointment
from datetime import date, timedelta
import json

def test_new_slot_interface():
    """Test the new slot time selection interface"""
    
    print("🧪 Testing New Slot Time Selection Interface")
    print("=" * 50)
    
    # Setup test client
    client = Client()
    User = get_user_model()
    
    # Create test user
    try:
        user = User.objects.get(username='testcustomer')
    except User.DoesNotExist:
        user = User.objects.create_user(
            username='testcustomer',
            email='test@customer.com',
            password='testpass123',
            role='customer',
            first_name='Test',
            last_name='Customer'
        )
    
    # Create test service
    try:
        category = ServiceCategory.objects.get(name='Test Category')
    except ServiceCategory.DoesNotExist:
        category = ServiceCategory.objects.create(
            name='Test Category',
            description='Test category for slot testing'
        )
    
    try:
        service = Service.objects.get(name='Test Slot Service')
    except Service.DoesNotExist:
        from datetime import timedelta
        service = Service.objects.create(
            name='Test Slot Service',
            description='Service for testing new slot interface',
            category=category,
            base_price=1500.00,
            estimated_duration=timedelta(hours=2),
            is_active=True
        )
    
    print(f"✅ Test setup complete")
    print(f"   User: {user.username} ({user.role})")
    print(f"   Service: {service.name} - ₹{service.base_price}")
    
    # Test 1: Login and access booking page
    print(f"\n🔐 Test 1: Login and access booking page")
    login_success = client.login(username='testcustomer', password='testpass123')
    print(f"   Login successful: {login_success}")
    
    booking_url = reverse('services:book_service', kwargs={'service_id': service.id})
    response = client.get(booking_url)
    print(f"   Booking page status: {response.status_code}")
    print(f"   URL: {booking_url}")
    
    # Test 2: Check API endpoint for available slots
    print(f"\n🕐 Test 2: Available slots API")
    tomorrow = date.today() + timedelta(days=1)
    api_url = reverse('appointments:available_slots_api')
    api_response = client.get(api_url, {'date': tomorrow.isoformat()})
    print(f"   API status: {api_response.status_code}")
    
    if api_response.status_code == 200:
        data = json.loads(api_response.content)
        print(f"   Available slots: {len(data.get('slots', []))}")
        print(f"   Total slots: {data.get('total_slots', 0)}")
        for slot in data.get('slots', [])[:3]:  # Show first 3
            print(f"     - {slot['display']} ({slot['time']})")
    
    # Test 3: Form validation with new structure
    print(f"\n📝 Test 3: Form submission")
    form_data = {
        'selected_service': service.id,
        'slot_date': tomorrow.isoformat(),
        'slot_time': '09:00',  # 9:00 AM slot
        'vehicle_make': 'Toyota',
        'vehicle_model': 'Camry',
        'vehicle_year': 2020,
        'vehicle_license': 'ABC-1234',
        'special_requirements': 'Test booking via new interface'
    }
    
    post_response = client.post(booking_url, form_data)
    print(f"   Form submission status: {post_response.status_code}")
    
    if post_response.status_code == 302:  # Redirect on success
        print(f"   ✅ Booking successful (redirected)")
        # Check if appointment was created
        appointment = Appointment.objects.filter(
            customer=user,
            selected_service=service,
            slot_date=tomorrow,
            slot_time='09:00'
        ).first()
        
        if appointment:
            print(f"   📅 Appointment created: #{appointment.id}")
            print(f"   📍 Date: {appointment.slot_date}")
            print(f"   🕐 Time: {appointment.get_slot_time_display()}")
            print(f"   🚗 Vehicle: {appointment.vehicle_year} {appointment.vehicle_make} {appointment.vehicle_model}")
    else:
        print(f"   ❌ Form submission failed")
        if hasattr(post_response, 'content'):
            content = post_response.content.decode()
            if 'error' in content.lower() or 'invalid' in content.lower():
                print(f"   Error in response content")
    
    # Test 4: Check slot occupancy after booking
    print(f"\n🔒 Test 4: Slot occupancy after booking")
    api_response_after = client.get(api_url, {'date': tomorrow.isoformat()})
    if api_response_after.status_code == 200:
        data_after = json.loads(api_response_after.content)
        available_after = len(data_after.get('slots', []))
        print(f"   Available slots after booking: {available_after}")
        
        # Check if 09:00 slot is now occupied
        all_slots = data_after.get('all_slots', [])
        slot_09 = next((s for s in all_slots if s['time'] == '09:00'), None)
        if slot_09:
            print(f"   09:00 slot occupied: {slot_09['occupied']}")
            if slot_09['occupied'] and slot_09['appointment']:
                print(f"   Appointment details: {slot_09['appointment']}")
    
    # Test 5: Template rendering and JavaScript integration
    print(f"\n🎨 Test 5: Template and JavaScript integration")
    final_response = client.get(booking_url)
    if final_response.status_code == 200:
        content = final_response.content.decode()
        
        # Check for key elements in the new interface
        checks = [
            ('Date input field', 'id_slot_date' in content),
            ('Time slot container', 'slot-selection-container' in content),
            ('JavaScript slot loading', 'fetchAvailableSlots' in content),
            ('Booking summary section', 'booking-summary' in content),
            ('Modern CSS styling', 'time-slot-card' in content),
            ('Loading animation', 'loading-spinner' in content)
        ]
        
        for check_name, check_result in checks:
            status = "✅" if check_result else "❌"
            print(f"   {status} {check_name}")
    
    print(f"\n🧹 Cleanup: Removing test data")
    # Clean up test appointment
    Appointment.objects.filter(customer=user, selected_service=service).delete()
    print(f"   Test appointments removed")
    
    print(f"\n🎉 New Slot Interface Test Complete!")
    print(f"=" * 50)

if __name__ == '__main__':
    test_new_slot_interface()