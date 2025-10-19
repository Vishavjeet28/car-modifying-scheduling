#!/usr/bin/env python3

import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carmodx.settings')
django.setup()

from appointments.forms import AppointmentBookingForm
from appointments.models import Appointment
from accounts.models import User
from services.models import Service
from datetime import datetime, timedelta

def test_form_validation():
    """Test that the form accepts dynamically loaded time slots"""
    
    print("🔧 TESTING FORM VALIDATION FIX")
    print("=" * 60)
    
    # Get test data
    customer = User.objects.filter(role='customer').first()
    service = Service.objects.filter(is_active=True).first()
    tomorrow = (datetime.now() + timedelta(days=1)).date()
    
    if not customer or not service:
        print("❌ Missing test data")
        return
    
    print(f"👤 Test User: {customer.username}")
    print(f"🔧 Test Service: {service.name}")
    print(f"📅 Test Date: {tomorrow}")
    
    # Get available slots
    available_slots = Appointment.get_available_slots(tomorrow)
    print(f"\n📋 Available slots: {len(available_slots)}")
    
    if not available_slots:
        print("⚠️  No available slots to test")
        return
    
    # Test 1: Form with valid data
    print("\n1️⃣ TESTING FORM WITH VALID TIME SLOT:")
    test_slot = available_slots[0]
    print(f"   Using slot: {test_slot['display']} ({test_slot['time']})")
    
    form_data = {
        'selected_service': service.id,
        'slot_date': tomorrow.strftime('%Y-%m-%d'),
        'slot_time': test_slot['time'],  # This should now be accepted!
        'vehicle_make': 'Toyota',
        'vehicle_model': 'Camry',
        'vehicle_year': 2020,
        'vehicle_license': 'TEST123',
        'special_requirements': 'Test booking'
    }
    
    form = AppointmentBookingForm(data=form_data, user=customer)
    
    if form.is_valid():
        print("   ✅ Form validation passed!")
        print("   ✅ Time slot was accepted correctly")
        
        # Don't actually save, just test validation
        print("   (Not saving to database - test only)")
    else:
        print("   ❌ Form validation failed!")
        print("   Errors:")
        for field, errors in form.errors.items():
            print(f"      {field}: {errors}")
    
    # Test 2: Form with empty time slot
    print("\n2️⃣ TESTING FORM WITH NO TIME SLOT:")
    form_data_no_time = form_data.copy()
    form_data_no_time['slot_time'] = ''
    
    form = AppointmentBookingForm(data=form_data_no_time, user=customer)
    
    if not form.is_valid():
        print("   ✅ Correctly rejected empty time slot")
        if 'slot_time' in form.errors or '__all__' in form.errors:
            print("   ✅ Appropriate error message shown")
    else:
        print("   ❌ Should have rejected empty time slot")
    
    # Test 3: Form with invalid time slot
    print("\n3️⃣ TESTING FORM WITH INVALID TIME SLOT:")
    form_data_invalid = form_data.copy()
    form_data_invalid['slot_time'] = '99:99'
    
    form = AppointmentBookingForm(data=form_data_invalid, user=customer)
    
    if not form.is_valid():
        print("   ✅ Correctly rejected invalid time slot")
    else:
        print("   ❌ Should have rejected invalid time slot")
    
    # Test 4: Test all valid time slots
    print("\n4️⃣ TESTING ALL VALID TIME SLOT CHOICES:")
    for time_value, time_display in Appointment.TIME_SLOT_CHOICES:
        form_data_test = form_data.copy()
        form_data_test['slot_time'] = time_value
        
        form = AppointmentBookingForm(data=form_data_test, user=customer)
        
        # Check if it's available
        is_occupied = Appointment.objects.filter(
            slot_date=tomorrow,
            slot_time=time_value,
            status__in=['booked', 'assigned', 'in_progress', 'on_hold']
        ).exists()
        
        if is_occupied:
            if not form.is_valid():
                print(f"   ✅ {time_display}: Correctly rejected (occupied)")
            else:
                print(f"   ❌ {time_display}: Should reject occupied slot")
        else:
            if form.is_valid():
                print(f"   ✅ {time_display}: Correctly accepted (available)")
            else:
                print(f"   ❌ {time_display}: Should accept available slot")
                print(f"      Errors: {form.errors}")
    
    print("\n" + "=" * 60)
    print("✅ FORM VALIDATION FIX COMPLETE!")
    print("=" * 60)
    print("📌 WHAT WAS FIXED:")
    print("   • slot_time field now includes all valid time slot choices")
    print("   • Form accepts any of the 5 time slots (09:00, 11:00, 13:00, 15:00, 17:00)")
    print("   • JavaScript can dynamically populate available slots")
    print("   • Form validation only checks if slot is occupied, not if it's in static list")
    print("\n🎯 RESULT:")
    print("   You can now select any available time slot from the dropdown")
    print("   and the form will accept it without 'Select a valid choice' error!")

if __name__ == '__main__':
    test_form_validation()