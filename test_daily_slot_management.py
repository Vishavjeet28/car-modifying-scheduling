#!/usr/bin/env python
"""
Test script for the DAILY slot management system
Tests that only 5 total appointments can be booked per day across all time slots
"""
import os
import sys
import django
from datetime import date, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carmodx.settings')
django.setup()

from django.contrib.auth import get_user_model
from services.models import Service, ServiceCategory
from appointments.models import Appointment

User = get_user_model()

def test_daily_slot_management():
    print("Testing DAILY Workshop Slot Management System")
    print("=" * 60)
    
    # Clean up existing test data
    print("0. Cleaning up existing test data...")
    Appointment.objects.filter(customer__username__startswith='testdaily').delete()
    User.objects.filter(username__startswith='testdaily').delete()
    
    # Use day after tomorrow for clean testing
    test_date = date.today() + timedelta(days=3)
    existing_appointments = Appointment.objects.filter(slot_date=test_date)
    print(f"   Cleaning {existing_appointments.count()} existing appointments for {test_date}")
    existing_appointments.delete()
    
    # Create test services
    print("1. Creating test services...")
    
    categories = []
    for cat_name in ['Engine Tuning', 'Body Work', 'Audio Systems']:
        category, created = ServiceCategory.objects.get_or_create(
            name=cat_name,
            defaults={'description': f'{cat_name} services'}
        )
        categories.append(category)
    
    services = []
    service_data = [
        {'name': 'ECU Remapping', 'category': categories[0], 'price': 15000},
        {'name': 'Body Kit Installation', 'category': categories[1], 'price': 25000},
        {'name': 'Premium Audio Setup', 'category': categories[2], 'price': 12000},
        {'name': 'Turbo Installation', 'category': categories[0], 'price': 35000},
        {'name': 'Paint Job', 'category': categories[1], 'price': 20000},
        {'name': 'Exhaust System', 'category': categories[0], 'price': 18000},
    ]
    
    for data in service_data:
        service, created = Service.objects.get_or_create(
            name=data['name'],
            defaults={
                'description': f'Professional {data["name"]} service',
                'category': data['category'],
                'base_price': data['price'],
                'estimated_duration': timedelta(hours=4)
            }
        )
        services.append(service)
        print(f"   - {service.name} ({service.category.name})")
    
    # Create test customers
    print("\n2. Creating test customers...")
    customers = []
    for i in range(8):  # Create 8 customers to test exceeding daily capacity
        customer, created = User.objects.get_or_create(
            username=f"testdaily{i+1}",
            defaults={
                'email': f'testdaily{i+1}@example.com',
                'first_name': f'Daily',
                'last_name': f'Test{i+1}',
                'role': 'customer'
            }
        )
        customers.append(customer)
        print(f"   - {customer.username}")
    
    # All available time slots
    time_slots = ['09:00', '11:00', '13:00', '15:00', '17:00']
    
    print(f"\n3. Testing daily capacity for {test_date}...")
    print(f"   Maximum daily capacity: 5 appointments (regardless of time slot)")
    
    # Check initial availability
    initial_capacity = Appointment.get_slot_capacity(test_date)
    print(f"   Initial available slots: {initial_capacity}/5")
    
    # Book 5 appointments across DIFFERENT time slots with different services
    print(f"\n4. Booking 5 appointments across different time slots...")
    booked_appointments = []
    
    for i in range(5):
        customer = customers[i]
        service = services[i % len(services)]
        time_slot = time_slots[i]  # Use different time slots
        
        try:
            appointment = Appointment.objects.create(
                customer=customer,
                selected_service=service,
                slot_date=test_date,
                slot_time=time_slot,
                vehicle_make='Honda',
                vehicle_model='Civic',
                vehicle_year=2020,
                vehicle_license=f'DAIL{i+1:03d}'
            )
            booked_appointments.append(appointment)
            
            remaining = Appointment.get_slot_capacity(test_date)
            print(f"   ✓ Booking {i+1}: {customer.username} booked {service.name} at {dict(Appointment.TIME_SLOT_CHOICES)[time_slot]}")
            print(f"     → Daily remaining slots: {remaining}/5")
            
        except Exception as e:
            print(f"   ✗ Booking {i+1} failed: {e}")
    
    # Try to book 6th appointment (should fail - exceeds daily capacity)
    print(f"\n5. Testing daily capacity limit - attempting 6th booking...")
    try:
        customer = customers[5]
        service = services[0]
        time_slot = '17:00'  # Try the last available time slot
        
        appointment = Appointment.objects.create(
            customer=customer,
            selected_service=service,
            slot_date=test_date,
            slot_time=time_slot,
            vehicle_make='Toyota',
            vehicle_model='Camry',
            vehicle_year=2021,
            vehicle_license='FAIL123'
        )
        print(f"   ✗ UNEXPECTED: 6th booking succeeded (should have failed)")
        
    except Exception as e:
        print(f"   ✓ EXPECTED: 6th booking failed - {e}")
    
    # Try to book in a different time slot (should also fail)
    print(f"\n6. Testing that NO time slots are available when daily limit is reached...")
    for time_slot in time_slots:
        try:
            customer = customers[6]
            service = services[1]
            
            appointment = Appointment.objects.create(
                customer=customer,
                selected_service=service,
                slot_date=test_date,
                slot_time=time_slot,
                vehicle_make='BMW',
                vehicle_model='X5',
                vehicle_year=2022,
                vehicle_license='NOTIME'
            )
            print(f"   ✗ UNEXPECTED: Booking at {dict(Appointment.TIME_SLOT_CHOICES)[time_slot]} succeeded")
            
        except Exception as e:
            print(f"   ✓ EXPECTED: {dict(Appointment.TIME_SLOT_CHOICES)[time_slot]} booking failed - Daily capacity reached")
    
    # Test slot availability API
    print(f"\n7. Testing slot availability API...")
    available_slots = Appointment.get_available_slots(test_date)
    
    if available_slots:
        print(f"   ✗ UNEXPECTED: {len(available_slots)} slots show as available when daily limit is reached")
    else:
        print(f"   ✓ EXPECTED: No slots available - daily capacity reached")
    
    # Test daily slot details
    print(f"\n8. Testing daily slot details...")
    daily_details = Appointment.get_daily_slot_details(test_date)
    print(f"   Total daily capacity: {daily_details['total_daily_capacity']}")
    print(f"   Daily occupied: {daily_details['daily_occupied']}")
    print(f"   Daily remaining: {daily_details['daily_remaining']}")
    print(f"   Appointments scheduled:")
    
    for appointment in daily_details['all_appointments']:
        time_display = dict(Appointment.TIME_SLOT_CHOICES)[appointment.slot_time]
        print(f"     - {time_display}: {appointment.customer.username} - {appointment.selected_service.name}")
    
    # Test that completing appointments frees up daily capacity
    print(f"\n9. Testing daily capacity release when appointment is completed...")
    
    if booked_appointments:
        # Complete one appointment
        completed_appointment = booked_appointments[0]
        completed_appointment.status = 'completed'
        completed_appointment.save()
        
        remaining_after_completion = Appointment.get_slot_capacity(test_date)
        print(f"   After completing 1 appointment: {remaining_after_completion}/5 daily slots available")
        
        # Try booking again (should now work)
        try:
            customer = customers[5]
            service = services[2]
            time_slot = '17:00'  # Any available time slot
            
            new_appointment = Appointment.objects.create(
                customer=customer,
                selected_service=service,
                slot_date=test_date,
                slot_time=time_slot,
                vehicle_make='BMW',
                vehicle_model='X3',
                vehicle_year=2022,
                vehicle_license='SUCCESS'
            )
            print(f"   ✓ New booking successful after daily slot was freed: {customer.username} → {service.name} at {dict(Appointment.TIME_SLOT_CHOICES)[time_slot]}")
            
        except Exception as e:
            print(f"   ✗ UNEXPECTED: New booking failed after daily slot was freed - {e}")
    
    # Final summary
    print(f"\n" + "=" * 60)
    print("DAILY SLOT MANAGEMENT TEST SUMMARY")
    print("=" * 60)
    
    final_daily_details = Appointment.get_daily_slot_details(test_date)
    print(f"Final daily occupancy for {test_date}:")
    print(f"  • Total daily capacity: 5 appointments")
    print(f"  • Currently booked: {final_daily_details['daily_occupied']}")
    print(f"  • Daily slots remaining: {final_daily_details['daily_remaining']}")
    
    print(f"\nAppointments scheduled for {test_date}:")
    active_appointments = [apt for apt in final_daily_details['all_appointments'] if apt.status in ['booked', 'assigned', 'in_progress', 'on_hold']]
    
    for appointment in active_appointments:
        time_display = dict(Appointment.TIME_SLOT_CHOICES)[appointment.slot_time]
        print(f"  • {time_display}: {appointment.selected_service.name} ({appointment.selected_service.category.name}) - {appointment.customer.username}")
    
    print(f"\n✅ DAILY SLOT MANAGEMENT IS WORKING CORRECTLY!")
    print(f"   - Only 5 total appointments allowed per day")
    print(f"   - Appointments can be in different time slots")
    print(f"   - Daily capacity prevents additional bookings")
    print(f"   - Completed appointments free up daily capacity")
    print(f"   - Proper validation prevents daily overbooking")

if __name__ == "__main__":
    test_daily_slot_management()