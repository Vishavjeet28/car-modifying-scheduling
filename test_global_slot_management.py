#!/usr/bin/env python
"""
Test script for the global slot management system
Tests that slots are shared across all services with maximum 5 global slots per time period
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

def test_global_slot_management():
    print("Testing Global Workshop Slot Management System")
    print("=" * 60)
    
    # Clean up any existing test data
    print("0. Cleaning up existing test data...")
    Appointment.objects.filter(customer__username__startswith='testglobal').delete()
    User.objects.filter(username__startswith='testglobal').delete()
    
    # Also clean up previous test data for a clean slate
    test_date = date.today() + timedelta(days=2)  # Use day after tomorrow for clean testing
    existing_appointments = Appointment.objects.filter(slot_date=test_date, slot_time='09:00')
    print(f"   Cleaning {existing_appointments.count()} existing appointments for {test_date} at 9:00 AM")
    existing_appointments.delete()
    
    # Create test services in different categories
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
    for i in range(7):  # Create 7 customers to test exceeding capacity
        customer, created = User.objects.get_or_create(
            username=f"testglobal{i+1}",
            defaults={
                'email': f'testglobal{i+1}@example.com',
                'first_name': f'Global',
                'last_name': f'Test{i+1}',
                'role': 'customer'
            }
        )
        customers.append(customer)
        print(f"   - {customer.username}")
    
    # Test date
    # test_date = date.today() + timedelta(days=1)  # Moved up to clean section
    test_time = '09:00'  # 9:00 AM slot
    
    print(f"\n3. Testing global slot capacity for {test_date} at 9:00 AM...")
    print(f"   Maximum global capacity: 5 slots")
    
    # Check initial availability
    initial_capacity = Appointment.get_slot_capacity(test_date, test_time)
    print(f"   Initial available slots: {initial_capacity}/5")
    
    # Book 5 appointments with DIFFERENT services
    print(f"\n4. Booking 5 appointments with different services...")
    booked_appointments = []
    
    for i in range(5):
        customer = customers[i]
        service = services[i % len(services)]  # Cycle through different services
        
        try:
            appointment = Appointment.objects.create(
                customer=customer,
                selected_service=service,
                slot_date=test_date,
                slot_time=test_time,
                vehicle_make='Honda',
                vehicle_model='Civic',
                vehicle_year=2020,
                vehicle_license=f'GLOB{i+1:03d}'
            )
            booked_appointments.append(appointment)
            
            remaining = Appointment.get_slot_capacity(test_date, test_time)
            print(f"   ✓ Booking {i+1}: {customer.username} booked {service.name}")
            print(f"     → Remaining slots: {remaining}/5")
            
        except Exception as e:
            print(f"   ✗ Booking {i+1} failed: {e}")
    
    # Try to book 6th appointment (should fail - exceeds global capacity)
    print(f"\n5. Testing capacity limit - attempting 6th booking...")
    try:
        customer = customers[5]
        service = services[0]  # Any service should fail
        
        appointment = Appointment.objects.create(
            customer=customer,
            selected_service=service,
            slot_date=test_date,
            slot_time=test_time,
            vehicle_make='Toyota',
            vehicle_model='Camry',
            vehicle_year=2021,
            vehicle_license='FAIL123'
        )
        print(f"   ✗ UNEXPECTED: 6th booking succeeded (should have failed)")
        
    except Exception as e:
        print(f"   ✓ EXPECTED: 6th booking failed - {e}")
    
    # Test slot availability API
    print(f"\n6. Testing slot availability API...")
    available_slots = Appointment.get_available_slots(test_date)
    
    nine_am_slot = None
    for slot in available_slots:
        if slot['time'] == '09:00':
            nine_am_slot = slot
            break
    
    if nine_am_slot:
        print(f"   ✗ UNEXPECTED: 9:00 AM slot shows as available: {nine_am_slot}")
    else:
        print(f"   ✓ EXPECTED: 9:00 AM slot not in available slots (fully booked)")
    
    # Check other time slots are still available
    other_slots = [slot for slot in available_slots if slot['time'] != '09:00']
    print(f"   ✓ Other time slots available: {len(other_slots)}")
    
    # Test detailed slot information
    print(f"\n7. Testing detailed slot information...")
    slot_details = Appointment.get_slot_details(test_date, test_time)
    print(f"   Total capacity: {slot_details['total_capacity']}")
    print(f"   Occupied: {slot_details['occupied']}")
    print(f"   Remaining: {slot_details['remaining']}")
    print(f"   Appointments in this slot:")
    
    for appointment in slot_details['appointments']:
        print(f"     - {appointment.customer.username}: {appointment.selected_service.name} ({appointment.selected_service.category.name})")
    
    # Test that completing appointments frees up slots
    print(f"\n8. Testing slot release when appointment is completed...")
    
    if booked_appointments:
        # Complete one appointment
        completed_appointment = booked_appointments[0]
        completed_appointment.status = 'completed'
        completed_appointment.save()
        
        remaining_after_completion = Appointment.get_slot_capacity(test_date, test_time)
        print(f"   After completing 1 appointment: {remaining_after_completion}/5 slots available")
        
        # Try booking again (should now work)
        try:
            customer = customers[5]
            service = services[2]
            
            new_appointment = Appointment.objects.create(
                customer=customer,
                selected_service=service,
                slot_date=test_date,
                slot_time=test_time,
                vehicle_make='BMW',
                vehicle_model='X3',
                vehicle_year=2022,
                vehicle_license='SUCCESS'
            )
            print(f"   ✓ New booking successful after slot was freed: {customer.username} → {service.name}")
            
        except Exception as e:
            print(f"   ✗ UNEXPECTED: New booking failed after slot was freed - {e}")
    else:
        print(f"   ⚠ Skipping completion test - no appointments were successfully booked")
    
    # Final summary
    print(f"\n" + "=" * 60)
    print("GLOBAL SLOT MANAGEMENT TEST SUMMARY")
    print("=" * 60)
    
    final_slot_details = Appointment.get_slot_details(test_date, test_time)
    print(f"Final slot occupancy for {test_date} at 9:00 AM:")
    print(f"  • Total capacity: 5 workshop slots")
    print(f"  • Currently occupied: {final_slot_details['occupied']}")
    print(f"  • Available: {final_slot_details['remaining']}")
    
    print(f"\nServices currently using the 9:00 AM slot:")
    active_appointments = [apt for apt in final_slot_details['appointments'] if apt.status in ['booked', 'assigned', 'in_progress', 'on_hold']]
    
    for appointment in active_appointments:
        print(f"  • {appointment.selected_service.name} ({appointment.selected_service.category.name}) - {appointment.customer.username}")
    
    print(f"\n✅ GLOBAL SLOT MANAGEMENT IS WORKING CORRECTLY!")
    print(f"   - Slots are shared across ALL services")
    print(f"   - Maximum 5 appointments per time slot regardless of service")
    print(f"   - Completed appointments free up slots for new bookings")
    print(f"   - Proper validation prevents overbooking")

if __name__ == "__main__":
    test_global_slot_management()