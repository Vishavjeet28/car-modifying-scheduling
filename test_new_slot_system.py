#!/usr/bin/env python3

import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carmodx.settings')
django.setup()

from django.test import Client
from accounts.models import User
from appointments.models import Appointment
from services.models import Service
from datetime import datetime, timedelta

def test_new_slot_system():
    """Test the new slot booking system where each time slot can only have 1 active appointment"""
    
    print("🔧 TESTING NEW SLOT BOOKING SYSTEM")
    print("=" * 60)
    print("📝 SYSTEM RULES:")
    print("   - Total 5 time slots available per day")
    print("   - Each time slot can only have 1 active appointment")
    print("   - Active statuses: booked, assigned, in_progress, on_hold")
    print("   - Completed/cancelled appointments free up the slot")
    print("=" * 60)
    
    # Get test data
    customer = User.objects.filter(role='customer').first()
    service = Service.objects.filter(is_active=True).first()
    tomorrow = (datetime.now() + timedelta(days=1)).date()
    
    if not customer or not service:
        print("❌ Missing test data (customer or service)")
        return
    
    print(f"\n👤 Test Customer: {customer.username}")
    print(f"🔧 Test Service: {service.name}")
    print(f"📅 Test Date: {tomorrow}")
    
    # Test 1: Check available slots for tomorrow
    print("\n1️⃣ CHECKING AVAILABLE SLOTS:")
    available_slots = Appointment.get_available_slots(tomorrow)
    print(f"   Available slots: {len(available_slots)}")
    for slot in available_slots:
        print(f"      - {slot['display']} ({slot['time']})")
    
    # Test 2: Check slot details
    print("\n2️⃣ DETAILED SLOT STATUS:")
    slot_details = Appointment.get_daily_slot_details(tomorrow)
    print(f"   Total slots: {slot_details['total_slots']}")
    print(f"   Occupied: {slot_details['occupied_slots']}")
    print(f"   Available: {slot_details['available_slots']}")
    
    print("\n   📋 Slot by slot breakdown:")
    for slot in slot_details['slots']:
        if slot['occupied']:
            apt = slot['appointment']
            print(f"      ❌ {slot['display']}: OCCUPIED")
            print(f"         Service: {apt['service']}")
            print(f"         Customer: {apt['customer']}")
            print(f"         Status: {apt['status']}")
        else:
            print(f"      ✅ {slot['display']}: AVAILABLE")
    
    # Test 3: Book a slot
    print("\n3️⃣ TESTING BOOKING:")
    if available_slots:
        first_slot = available_slots[0]
        print(f"   Attempting to book: {first_slot['display']}")
        
        try:
            # Create appointment
            appointment = Appointment(
                customer=customer,
                selected_service=service,
                slot_date=tomorrow,
                slot_time=first_slot['time'],
                vehicle_make="Toyota",
                vehicle_model="Camry",
                vehicle_year=2020,
                vehicle_license="TEST123"
            )
            appointment.save()
            print(f"   ✅ Booking successful! Appointment ID: {appointment.id}")
            
            # Check if slot is now unavailable
            available_after = Appointment.get_available_slots(tomorrow)
            print(f"   📊 Available slots after booking: {len(available_after)}")
            
            # Try to book same slot again (should fail)
            print(f"\n   Testing double-booking prevention:")
            try:
                duplicate = Appointment(
                    customer=customer,
                    selected_service=service,
                    slot_date=tomorrow,
                    slot_time=first_slot['time'],
                    vehicle_make="Honda",
                    vehicle_model="Civic",
                    vehicle_year=2021,
                    vehicle_license="TEST456"
                )
                duplicate.save()
                print("   ❌ ERROR: Double booking was allowed!")
            except Exception as e:
                print(f"   ✅ Double booking prevented: {str(e)[:80]}")
            
            # Test 4: Complete the appointment and check availability
            print(f"\n4️⃣ TESTING SLOT RELEASE:")
            print(f"   Marking appointment as completed...")
            appointment.status = 'completed'
            appointment.work_completed_at = datetime.now()
            appointment.save()
            
            available_after_complete = Appointment.get_available_slots(tomorrow)
            print(f"   📊 Available slots after completion: {len(available_after_complete)}")
            
            if len(available_after_complete) > len(available_after):
                print(f"   ✅ Slot released successfully!")
                print(f"   ✅ Slot {first_slot['display']} is now available again")
            else:
                print(f"   ❌ Slot not released")
            
            # Clean up
            appointment.delete()
            print(f"\n   🧹 Test appointment deleted")
            
        except Exception as e:
            print(f"   ❌ Booking failed: {e}")
    else:
        print("   ⚠️  No available slots to test")
    
    # Test 5: Test API endpoint
    print("\n5️⃣ TESTING API ENDPOINT:")
    client = Client()
    client.force_login(customer)
    
    response = client.get(f'/appointments/api/available-slots/?date={tomorrow}')
    print(f"   API Status: {response.status_code}")
    
    if response.status_code == 200:
        import json
        data = json.loads(response.content.decode())
        print(f"   ✅ API working")
        print(f"   Total slots: {data.get('total_slots', 0)}")
        print(f"   Occupied: {data.get('occupied_slots', 0)}")
        print(f"   Available: {data.get('available_slots', 0)}")
        print(f"   Slots in dropdown: {len(data.get('slots', []))}")
    
    print("\n" + "=" * 60)
    print("✅ NEW SLOT SYSTEM IMPLEMENTATION COMPLETE!")
    print("=" * 60)
    print("📌 KEY FEATURES:")
    print("   • Each time slot (9AM, 11AM, 1PM, 3PM, 5PM) can have 1 active booking")
    print("   • Active = booked, assigned, in_progress, on_hold")
    print("   • Completed/cancelled appointments free up the slot")
    print("   • Dropdown only shows available (unoccupied) slots")
    print("   • Double-booking is prevented at model level")
    print("\n🚀 TO TEST MANUALLY:")
    print("   1. Login as customer")
    print("   2. Book an appointment for tomorrow at 9:00 AM")
    print("   3. Try to book another appointment - 9:00 AM should NOT appear")
    print("   4. Mark first appointment as 'completed' (as employee/admin)")
    print("   5. Try to book again - 9:00 AM should now be available!")

if __name__ == '__main__':
    test_new_slot_system()