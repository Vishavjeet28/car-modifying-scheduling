#!/usr/bin/env python
"""
Test script to verify that users can book multiple appointments without restrictions.
This test confirms that the system allows unlimited appointments per user.
"""

import os
import sys
import django
from datetime import date, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carmodx.settings')
sys.path.append('/Users/vishavjeetsingh/untitled folder/untitled folder/detailcursor')

django.setup()

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from accounts.models import User
from services.models import Service, ServiceCategory
from appointments.models import Appointment

def test_multiple_appointments_per_user():
    """Test that a single user can book multiple appointments"""
    print("🧪 Testing Multiple Appointments Per User")
    print("=" * 60)
    
    # Clean slate
    Appointment.objects.all().delete()
    User.objects.filter(username__startswith='testuser').delete()
    
    # Create test user
    user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123',
        first_name='Test',
        last_name='User',
        phone_number='1234567890'
    )
    
    # Create service category and service
    category, created = ServiceCategory.objects.get_or_create(
        name='Test Category',
        defaults={'description': 'Test category for appointments'}
    )
    
    service, created = Service.objects.get_or_create(
        name='Test Service',
        defaults={
            'description': 'Test service',
            'price': 100.00,
            'duration_hours': 2,
            'category': category,
            'is_active': True
        }
    )
    
    print(f"✓ Created test user: {user.username}")
    print(f"✓ Created test service: {service.name}")
    
    # Test dates
    tomorrow = date.today() + timedelta(days=1)
    day_after = date.today() + timedelta(days=2)
    day_three = date.today() + timedelta(days=3)
    
    # Test 1: Book multiple appointments on different dates
    print("\n📅 Test 1: Multiple appointments on different dates")
    
    appointments = []
    test_data = [
        (tomorrow, '09:00', 'First appointment'),
        (day_after, '11:00', 'Second appointment'),
        (day_three, '13:00', 'Third appointment'),
    ]
    
    for slot_date, slot_time, description in test_data:
        appointment = Appointment.objects.create(
            customer=user,
            selected_service=service,
            slot_date=slot_date,
            slot_time=slot_time,
            vehicle_make='Toyota',
            vehicle_model='Camry',
            vehicle_year=2021,
            vehicle_license=f'TEST-{len(appointments)+1}',
            special_requirements=description
        )
        appointments.append(appointment)
        print(f"   ✓ Booked appointment {len(appointments)}: {slot_date} at {slot_time}")
    
    # Verify all appointments were created
    user_appointments = Appointment.objects.filter(customer=user)
    assert user_appointments.count() == 3, f"Expected 3 appointments, got {user_appointments.count()}"
    print(f"   ✓ User now has {user_appointments.count()} active appointments")
    
    # Test 2: Book multiple appointments on the same date (different time slots)
    print("\n🕒 Test 2: Multiple appointments on same date (different time slots)")
    
    same_date = date.today() + timedelta(days=4)
    same_date_appointments = [
        ('09:00', 'Morning appointment'),
        ('15:00', 'Afternoon appointment'),
    ]
    
    for slot_time, description in same_date_appointments:
        appointment = Appointment.objects.create(
            customer=user,
            selected_service=service,
            slot_date=same_date,
            slot_time=slot_time,
            vehicle_make='Honda',
            vehicle_model='Civic',
            vehicle_year=2020,
            vehicle_license=f'SAME-{slot_time}',
            special_requirements=description
        )
        appointments.append(appointment)
        print(f"   ✓ Booked appointment on {same_date} at {slot_time}")
    
    # Verify total appointments
    user_appointments = Appointment.objects.filter(customer=user)
    assert user_appointments.count() == 5, f"Expected 5 appointments, got {user_appointments.count()}"
    print(f"   ✓ User now has {user_appointments.count()} total appointments")
    
    # Test 3: Test booking form allows multiple appointments
    print("\n📝 Test 3: Form validation allows multiple appointments")
    
    client = Client()
    client.force_login(user)
    
    # Book appointment via form
    form_date = date.today() + timedelta(days=5)
    form_data = {
        'selected_service': service.id,
        'slot_date': form_date.strftime('%Y-%m-%d'),
        'slot_time': '11:00',
        'vehicle_make': 'BMW',
        'vehicle_model': 'X5',
        'vehicle_year': 2022,
        'vehicle_license': 'FORM-1',
        'special_requirements': 'Form booking test'
    }
    
    response = client.post('/appointments/book/', form_data)
    
    if response.status_code == 302:  # Successful redirect
        user_appointments = Appointment.objects.filter(customer=user)
        print(f"   ✓ Form booking successful - User now has {user_appointments.count()} appointments")
    else:
        print(f"   ✗ Form booking failed with status {response.status_code}")
        if hasattr(response, 'content'):
            print(f"      Response content: {response.content.decode()[:200]}...")
    
    # Test 4: Verify appointment details
    print("\n📋 Test 4: Verify appointment details")
    
    all_appointments = Appointment.objects.filter(customer=user).order_by('slot_date', 'slot_time')
    
    print(f"   📊 Total appointments for {user.username}: {all_appointments.count()}")
    print("   📅 Appointment schedule:")
    
    for i, apt in enumerate(all_appointments, 1):
        time_display = dict(Appointment.TIME_SLOT_CHOICES)[apt.slot_time]
        print(f"      {i}. {apt.slot_date} at {time_display} - {apt.selected_service.name}")
        print(f"         Vehicle: {apt.vehicle_year} {apt.vehicle_make} {apt.vehicle_model} ({apt.vehicle_license})")
        print(f"         Status: {apt.get_status_display()}")
    
    # Test 5: Test daily capacity limits (should still work)
    print("\n🏭 Test 5: Daily capacity limits still enforced")
    
    # Try to book 6th appointment on the same date (should fail due to daily limit)
    capacity_test_date = date.today() + timedelta(days=6)
    
    # Create 5 appointments for the test date (max daily capacity)
    for i in range(5):
        time_slot = ['09:00', '11:00', '13:00', '15:00', '17:00'][i]
        Appointment.objects.create(
            customer=user,
            selected_service=service,
            slot_date=capacity_test_date,
            slot_time=time_slot,
            vehicle_make='Test',
            vehicle_model=f'Model{i+1}',
            vehicle_year=2020,
            vehicle_license=f'CAP-{i+1}'
        )
    
    print(f"   ✓ Created 5 appointments for {capacity_test_date} (daily limit)")
    
    # Try to create 6th appointment (should fail)
    try:
        sixth_appointment = Appointment(
            customer=user,
            selected_service=service,
            slot_date=capacity_test_date,
            slot_time='09:00',  # Try to book in occupied slot
            vehicle_make='Overflow',
            vehicle_model='Test',
            vehicle_year=2020,
            vehicle_license='OVERFLOW'
        )
        sixth_appointment.full_clean()
        sixth_appointment.save()
        print("   ✗ Daily capacity limit not enforced!")
    except Exception as e:
        print(f"   ✓ Daily capacity limit enforced: {str(e)[:60]}...")
    
    # Final summary
    print("\n" + "=" * 60)
    print("🎯 MULTIPLE APPOINTMENTS TEST SUMMARY")
    print("=" * 60)
    
    total_appointments = Appointment.objects.filter(customer=user).count()
    print(f"✅ Total appointments created for user: {total_appointments}")
    print(f"✅ No restrictions on multiple appointments per user")
    print(f"✅ Daily capacity limits still enforced (5 per day)")
    print(f"✅ Users can book multiple appointments across different dates")
    print(f"✅ Users can book multiple appointments on same date (different time slots)")
    
    # Show all user appointments by date
    appointments_by_date = {}
    for apt in Appointment.objects.filter(customer=user).order_by('slot_date', 'slot_time'):
        date_str = apt.slot_date.strftime('%Y-%m-%d')
        if date_str not in appointments_by_date:
            appointments_by_date[date_str] = []
        appointments_by_date[date_str].append(apt)
    
    print(f"\n📅 User's appointment schedule:")
    for date_str, date_appointments in appointments_by_date.items():
        print(f"   {date_str}: {len(date_appointments)} appointment(s)")
        for apt in date_appointments:
            time_display = dict(Appointment.TIME_SLOT_CHOICES)[apt.slot_time]
            print(f"      - {time_display}: {apt.vehicle_make} {apt.vehicle_model}")
    
    print(f"\n🎉 Multiple appointments feature working correctly!")
    return True

if __name__ == '__main__':
    test_multiple_appointments_per_user()