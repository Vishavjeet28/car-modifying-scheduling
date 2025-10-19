#!/usr/bin/env python3

"""
Test the complete booking flow to identify issues
"""

import os
import sys
import django

# Setup Django environment
sys.path.append('/Users/vishavjeetsingh/untitled folder/untitled folder/detailcursor')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carmodx.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from services.models import Service
from appointments.models import Appointment
from datetime import date, timedelta
import json

def test_booking_process():
    """Test the complete booking process"""
    
    print("🧪 Testing Complete Booking Process")
    print("=" * 50)
    
    client = Client()
    User = get_user_model()
    
    # Check if we have a test user
    try:
        user = User.objects.get(username='testcustomer')
        print(f"✅ Found test user: {user.username}")
    except User.DoesNotExist:
        print("❌ No test user found. Creating one...")
        user = User.objects.create_user(
            username='testcustomer',
            email='test@customer.com',
            password='testpass123',
            role='customer',
            first_name='Test',
            last_name='Customer'
        )
        print(f"✅ Created test user: {user.username}")
    
    # Check services
    service = Service.objects.filter(id=7, is_active=True).first()
    if not service:
        services = Service.objects.filter(is_active=True)[:1]
        if services:
            service = services[0]
            print(f"⚠️  Service ID 7 not found, using service ID {service.id}: {service.name}")
        else:
            print("❌ No active services found!")
            return
    else:
        print(f"✅ Found service: {service.name} (ID: {service.id})")
    
    # Test 1: Access booking page without login
    print(f"\n🔐 Test 1: Access booking page without login")
    booking_url = reverse('services:book_service', kwargs={'service_id': service.id})
    response = client.get(booking_url)
    print(f"   URL: {booking_url}")
    print(f"   Status: {response.status_code}")
    if response.status_code == 302:
        print(f"   ✅ Redirected to login (expected)")
    
    # Test 2: Login and access booking page
    print(f"\n🔐 Test 2: Login and access booking page")
    login_success = client.login(username='testcustomer', password='testpass123')
    print(f"   Login success: {login_success}")
    
    if login_success:
        response = client.get(booking_url)
        print(f"   Booking page status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.content.decode()
            print(f"   ✅ Page loaded successfully")
            
            # Check for form elements
            form_checks = [
                ('Date input', 'id_slot_date' in content),
                ('Time input', 'id_slot_time' in content),
                ('Vehicle make', 'id_vehicle_make' in content),
                ('Submit button', 'book-btn' in content),
                ('JavaScript', 'fetchAvailableSlots' in content)
            ]
            
            print(f"   Form elements:")
            for check_name, check_result in form_checks:
                status = "✅" if check_result else "❌"
                print(f"     {status} {check_name}")
    
    # Test 3: Check API endpoint
    print(f"\n📡 Test 3: Check available slots API")
    tomorrow = date.today() + timedelta(days=1)
    api_url = reverse('appointments:available_slots_api')
    api_response = client.get(api_url, {'date': tomorrow.isoformat()})
    print(f"   API URL: {api_url}?date={tomorrow}")
    print(f"   API Status: {api_response.status_code}")
    
    if api_response.status_code == 200:
        data = json.loads(api_response.content)
        print(f"   Available slots: {len(data.get('slots', []))}")
        if data.get('slots'):
            print(f"   First slot: {data['slots'][0]}")
    
    # Test 4: Try to submit booking form
    print(f"\n📝 Test 4: Submit booking form")
    form_data = {
        'selected_service': service.id,
        'slot_date': tomorrow.isoformat(),
        'slot_time': '09:00',
        'vehicle_make': 'Toyota',
        'vehicle_model': 'Camry',
        'vehicle_year': 2020,
        'vehicle_license': 'TEST-123',
        'special_requirements': 'Test booking'
    }
    
    print(f"   Form data: {form_data}")
    post_response = client.post(booking_url, form_data)
    print(f"   Submit status: {post_response.status_code}")
    
    if post_response.status_code == 302:
        print(f"   ✅ Form submitted successfully (redirect)")
        # Check if appointment was created
        appointment = Appointment.objects.filter(
            customer=user,
            slot_date=tomorrow,
            slot_time='09:00'
        ).first()
        
        if appointment:
            print(f"   ✅ Appointment created: #{appointment.id}")
            print(f"   📅 Date: {appointment.slot_date}")
            print(f"   🕐 Time: {appointment.get_slot_time_display()}")
            
            # Clean up
            appointment.delete()
            print(f"   🧹 Test appointment deleted")
        else:
            print(f"   ❌ No appointment found in database")
    
    elif post_response.status_code == 200:
        print(f"   ❌ Form submission failed (stayed on same page)")
        content = post_response.content.decode()
        if 'error' in content.lower() or 'invalid' in content.lower():
            print(f"   ❌ Form contains errors")
    
    print(f"\n💡 Debugging Tips:")
    print(f"1. Open browser to: http://127.0.0.1:8000{booking_url}")
    print(f"2. Login with: testcustomer / testpass123")
    print(f"3. Open browser console (F12)")
    print(f"4. Select date: {tomorrow}")
    print(f"5. Click on a time slot")
    print(f"6. Check console for debug messages")
    print(f"7. Try to submit the form")

if __name__ == '__main__':
    test_booking_process()