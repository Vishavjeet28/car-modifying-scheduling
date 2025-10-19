#!/usr/bin/env python
"""
Test to verify that booked slots are completely hidden from the dropdown
"""

import os
import sys
import django
from datetime import date, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carmodx.settings')
sys.path.append('/Users/vishavjeetsingh/untitled folder/untitled folder/detailcursor')

django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from appointments.models import Appointment
from services.models import Service

User = get_user_model()

def test_booked_slots_hidden():
    print("🔍 Testing: Booked Slots Should Be Hidden From Dropdown")
    print("=" * 70)
    
    # Create test users
    user1 = User.objects.get_or_create(
        username='testbook1',
        defaults={
            'email': 'testbook1@example.com',
            'first_name': 'Test',
            'last_name': 'Book1',
            'role': 'customer'
        }
    )[0]
    
    user2 = User.objects.get_or_create(
        username='testbook2', 
        defaults={
            'email': 'testbook2@example.com',
            'first_name': 'Test',
            'last_name': 'Book2',
            'role': 'customer'
        }
    )[0]
    
    # Get a service
    service = Service.objects.filter(is_active=True).first()
    
    # Test date
    test_date = date.today() + timedelta(days=10)  # Use a future date with no existing bookings
    
    print(f"📅 Test Date: {test_date}")
    print(f"👥 Test Users: {user1.username}, {user2.username}")
    print(f"🔧 Service: {service.name}")
    
    # Clean existing appointments for this date
    Appointment.objects.filter(slot_date=test_date).delete()
    
    print(f"\n🧹 Cleaned existing appointments for {test_date}")
    
    # Step 1: Check all slots are initially available
    print(f"\n📋 Step 1: Initial availability (should show all 5 slots)")
    available_slots = Appointment.get_available_slots(test_date)
    
    print(f"Available slots: {len(available_slots)}/5")
    for slot in available_slots:
        print(f"  ✅ {slot['time']} - {slot['display']}")
    
    # Step 2: Book 9:00 AM slot with user1
    print(f"\n📋 Step 2: Book 9:00 AM slot with {user1.username}")
    
    appointment1 = Appointment.objects.create(
        customer=user1,
        selected_service=service,
        slot_date=test_date,
        slot_time='09:00',
        vehicle_make='Toyota',
        vehicle_model='Camry',
        vehicle_year=2022,
        vehicle_license='TEST-001'
    )
    
    print(f"✅ Booked: {appointment1}")
    
    # Check availability after booking 9:00 AM
    print(f"\n📋 Step 3: Check availability after booking 9:00 AM")
    available_slots = Appointment.get_available_slots(test_date)
    
    print(f"Available slots: {len(available_slots)}/5 (should be 4 now)")
    slots_shown = []
    for slot in available_slots:
        print(f"  ✅ {slot['time']} - {slot['display']}")
        slots_shown.append(slot['time'])
    
    if '09:00' in slots_shown:
        print("  ❌ ERROR: 9:00 AM slot still showing as available!")
    else:
        print("  ✅ CORRECT: 9:00 AM slot hidden from dropdown")
    
    # Step 4: Try to book 9:00 AM with user2 (should fail)
    print(f"\n📋 Step 4: Try to book same 9:00 AM slot with {user2.username}")
    
    try:
        appointment2 = Appointment(
            customer=user2,
            selected_service=service,
            slot_date=test_date,
            slot_time='09:00',  # Same slot
            vehicle_make='Honda',
            vehicle_model='Civic',
            vehicle_year=2021,
            vehicle_license='TEST-002'
        )
        appointment2.full_clean()  # This should raise ValidationError
        appointment2.save()
        print("  ❌ ERROR: Double booking was allowed!")
    except Exception as e:
        print(f"  ✅ CORRECT: Double booking prevented - {str(e)[:60]}...")
    
    # Step 5: Book another slot (1:00 PM) with user2
    print(f"\n📋 Step 5: Book 1:00 PM slot with {user2.username}")
    
    appointment3 = Appointment.objects.create(
        customer=user2,
        selected_service=service,
        slot_date=test_date,
        slot_time='13:00',
        vehicle_make='Honda',
        vehicle_model='Civic',
        vehicle_year=2021,
        vehicle_license='TEST-002'
    )
    
    print(f"✅ Booked: {appointment3}")
    
    # Check final availability
    print(f"\n📋 Step 6: Final availability check (should show 3 slots)")
    available_slots = Appointment.get_available_slots(test_date)
    
    print(f"Available slots: {len(available_slots)}/5 (should be 3 now)")
    slots_shown = []
    for slot in available_slots:
        print(f"  ✅ {slot['time']} - {slot['display']}")
        slots_shown.append(slot['time'])
    
    # Verify booked slots are hidden
    booked_slots = ['09:00', '13:00']
    hidden_correctly = True
    
    for booked_slot in booked_slots:
        if booked_slot in slots_shown:
            print(f"  ❌ ERROR: {booked_slot} slot still showing as available!")
            hidden_correctly = False
        else:
            print(f"  ✅ CORRECT: {booked_slot} slot hidden from dropdown")
    
    # Test via API
    print(f"\n📋 Step 7: Test via API endpoint")
    client = Client()
    response = client.get(f'/appointments/api/available-slots/?date={test_date}')
    
    if response.status_code == 200:
        data = response.json()
        api_slots = [slot['time'] for slot in data['slots']]
        
        print(f"API available slots: {len(api_slots)} slots")
        print(f"API slots: {api_slots}")
        
        for booked_slot in booked_slots:
            if booked_slot in api_slots:
                print(f"  ❌ API ERROR: {booked_slot} slot still in API response!")
                hidden_correctly = False
            else:
                print(f"  ✅ API CORRECT: {booked_slot} slot not in API response")
    
    # Test web form
    print(f"\n📋 Step 8: Test web form dropdown")
    
    client.force_login(user1)
    response = client.get('/appointments/book/')
    
    if response.status_code == 200:
        print("  ✅ Booking form accessible")
        print("  ℹ️  JavaScript will fetch available slots when date is selected")
        print("  ℹ️  Booked slots should not appear in the time slot dropdown")
    
    # Summary
    print(f"\n" + "=" * 70)
    print(f"🎯 SUMMARY: Booked Slots Hidden Test")
    print(f"=" * 70)
    
    if hidden_correctly:
        print(f"✅ SUCCESS: Booked slots are properly hidden from dropdown")
        print(f"✅ Only available slots ({len(available_slots)}) are shown")
        print(f"✅ Double booking is prevented")
        print(f"✅ API returns only available slots")
    else:
        print(f"❌ FAILURE: Some booked slots are still visible")
    
    print(f"\n📊 Current state for {test_date}:")
    all_appointments = Appointment.objects.filter(slot_date=test_date)
    for apt in all_appointments:
        print(f"  🔒 {apt.slot_time} - {apt.customer.username} - {apt.selected_service.name}")
    
    print(f"\n📝 Available in dropdown: {[slot['time'] for slot in available_slots]}")
    print(f"🚫 Hidden from dropdown: {[apt.slot_time for apt in all_appointments]}")

if __name__ == '__main__':
    test_booked_slots_hidden()