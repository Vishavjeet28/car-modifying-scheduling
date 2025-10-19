#!/usr/bin/env python
"""
Test script for the appointment booking system
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

def test_appointment_system():
    print("Testing CarModX Appointment Booking System")
    print("=" * 50)
    
    # Create test data
    print("1. Creating test data...")
    
    # Create a service category
    category, created = ServiceCategory.objects.get_or_create(
        name="Engine Modifications",
        defaults={'description': 'Engine tuning and modifications'}
    )
    
    # Create a service
    service, created = Service.objects.get_or_create(
        name="Turbo Installation",
        defaults={
            'description': 'Professional turbo installation service',
            'category': category,
            'base_price': 50000.00,
            'estimated_duration': '04:00:00'  # 4 hours
        }
    )
    
    # Create a test customer
    customer, created = User.objects.get_or_create(
        username="testcustomer",
        defaults={
            'email': 'customer@test.com',
            'first_name': 'Test',
            'last_name': 'Customer',
            'role': 'customer'
        }
    )
    
    print(f"   - Service: {service.name}")
    print(f"   - Customer: {customer.username}")
    
    # Test slot availability
    print("\n2. Testing slot availability...")
    tomorrow = date.today() + timedelta(days=1)
    
    available_slots = Appointment.get_available_slots(tomorrow)
    print(f"   - Available slots for {tomorrow}: {len(available_slots)}")
    
    for slot in available_slots:
        print(f"     * {slot['display']}: {slot['remaining']}/5 slots available")
    
    # Test booking appointments
    print("\n3. Testing appointment booking...")
    
    try:
        appointment = Appointment.objects.create(
            customer=customer,
            selected_service=service,
            slot_date=tomorrow,
            slot_time='09:00',  # 9:00 AM
            vehicle_make='Toyota',
            vehicle_model='Camry',
            vehicle_year=2020,
            vehicle_license='ABC-1234',
            special_requirements='Please use premium parts'
        )
        print(f"   ✓ Appointment #{appointment.id} created successfully")
        print(f"     - Date: {appointment.slot_date}")
        print(f"     - Time: {appointment.get_slot_time_display()}")
        print(f"     - Status: {appointment.get_status_display()}")
        
    except Exception as e:
        print(f"   ✗ Error creating appointment: {e}")
    
    # Test slot capacity after booking
    print("\n4. Testing slot capacity after booking...")
    remaining_capacity = Appointment.get_slot_capacity(tomorrow, '09:00')
    print(f"   - Remaining capacity for 9:00 AM: {remaining_capacity}/5")
    
    # Test booking multiple appointments in same slot
    print("\n5. Testing multiple bookings in same slot...")
    
    for i in range(2, 6):  # Book 4 more appointments (total 5)
        try:
            customer_i, created = User.objects.get_or_create(
                username=f"customer{i}",
                defaults={
                    'email': f'customer{i}@test.com',
                    'role': 'customer'
                }
            )
            
            appointment = Appointment.objects.create(
                customer=customer_i,
                selected_service=service,
                slot_date=tomorrow,
                slot_time='09:00',
                vehicle_make='Honda',
                vehicle_model='Civic',
                vehicle_year=2019,
                vehicle_license=f'XYZ-{i}234'
            )
            print(f"   ✓ Appointment #{appointment.id} for customer{i} created")
            
        except Exception as e:
            print(f"   ✗ Error creating appointment for customer{i}: {e}")
    
    # Check final capacity
    final_capacity = Appointment.get_slot_capacity(tomorrow, '09:00')
    print(f"\n   - Final capacity for 9:00 AM: {final_capacity}/5")
    
    # Test booking when slot is full
    print("\n6. Testing booking when slot is full...")
    try:
        customer_full, created = User.objects.get_or_create(
            username="customerfull",
            defaults={'email': 'full@test.com', 'role': 'customer'}
        )
        
        appointment = Appointment.objects.create(
            customer=customer_full,
            selected_service=service,
            slot_date=tomorrow,
            slot_time='09:00',
            vehicle_make='BMW',
            vehicle_model='X5',
            vehicle_year=2021,
            vehicle_license='FULL-123'
        )
        print(f"   ✗ Unexpected: Appointment created when slot should be full")
        
    except Exception as e:
        print(f"   ✓ Expected error when slot is full: {e}")
    
    # Test duplicate booking for same customer on same date
    print("\n7. Testing duplicate booking prevention...")
    try:
        duplicate_appointment = Appointment.objects.create(
            customer=customer,  # Same customer as first appointment
            selected_service=service,
            slot_date=tomorrow,  # Same date
            slot_time='11:00',   # Different time
            vehicle_make='Toyota',
            vehicle_model='Prius',
            vehicle_year=2022,
            vehicle_license='DUP-123'
        )
        print(f"   ✗ Unexpected: Duplicate appointment created")
        
    except Exception as e:
        print(f"   ✓ Expected error for duplicate booking: {e}")
    
    # Summary
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    
    total_appointments = Appointment.objects.filter(slot_date=tomorrow).count()
    print(f"Total appointments for {tomorrow}: {total_appointments}")
    
    for slot_time, slot_display in Appointment.TIME_SLOT_CHOICES:
        count = Appointment.objects.filter(
            slot_date=tomorrow, 
            slot_time=slot_time,
            status='booked'
        ).count()
        remaining = 5 - count
        print(f"{slot_display}: {count}/5 booked, {remaining} remaining")
    
    print("\n✓ Appointment booking system test completed!")

if __name__ == "__main__":
    test_appointment_system()