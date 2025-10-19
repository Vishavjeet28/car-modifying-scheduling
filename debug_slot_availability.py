#!/usr/bin/env python
"""
Debug script to check slot availability issues
"""

import os
import sys
import django
from datetime import date, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carmodx.settings')
sys.path.append('/Users/vishavjeetsingh/untitled folder/untitled folder/detailcursor')

django.setup()

from appointments.models import Appointment

def debug_slot_availability():
    print("🔍 Debugging Slot Availability Issues")
    print("=" * 60)
    
    today = date.today()
    tomorrow = today + timedelta(days=1)
    
    print("=== Current Appointments in Database ===")
    all_appointments = Appointment.objects.all().order_by('slot_date', 'slot_time')
    
    for apt in all_appointments:
        print(f"{apt.slot_date} at {apt.slot_time} - {apt.customer.username} - {apt.selected_service.name} - Status: {apt.status}")
    
    print(f"\n=== Testing Slot Availability for {tomorrow} ===")
    
    # Test the get_available_slots method
    available_slots = Appointment.get_available_slots(tomorrow)
    print(f"Available slots returned by get_available_slots(): {len(available_slots)}")
    
    for slot in available_slots:
        print(f"  - {slot['time']} ({slot['display']}) - Remaining: {slot['remaining']}")
    
    # Check what's actually in the database for tomorrow
    tomorrow_appointments = Appointment.objects.filter(
        slot_date=tomorrow,
        status__in=['booked', 'assigned', 'in_progress', 'on_hold']
    )
    
    print(f"\nTomorrow ({tomorrow}) has {tomorrow_appointments.count()} appointments:")
    for apt in tomorrow_appointments:
        print(f"  - {apt.slot_time} ({apt.get_slot_time_display()}) - {apt.customer.username} - {apt.selected_service.name}")
    
    # Check each time slot individually
    print(f"\n=== Time Slot Occupancy Check for {tomorrow} ===")
    for slot_time, slot_display in Appointment.TIME_SLOT_CHOICES:
        occupied = Appointment.objects.filter(
            slot_date=tomorrow,
            slot_time=slot_time,
            status__in=['booked', 'assigned', 'in_progress', 'on_hold']
        ).exists()
        
        count = Appointment.objects.filter(
            slot_date=tomorrow,
            slot_time=slot_time,
            status__in=['booked', 'assigned', 'in_progress', 'on_hold']
        ).count()
        
        print(f"{slot_time} ({slot_display}): {'OCCUPIED' if occupied else 'AVAILABLE'} (Count: {count})")
    
    # Test the API response format
    print(f"\n=== Testing API Response ===")
    daily_details = Appointment.get_daily_slot_details(tomorrow)
    
    print(f"Daily details for {tomorrow}:")
    print(f"  - Daily occupied: {daily_details['daily_occupied']}")
    print(f"  - Daily remaining: {daily_details['daily_remaining']}")
    
    print(f"\nTime slots breakdown:")
    for slot_time, slot_display in Appointment.TIME_SLOT_CHOICES:
        slot_data = daily_details['time_slots'][slot_time]
        print(f"  {slot_time} ({slot_display}):")
        print(f"    - Appointments count: {len(slot_data['appointments'])}")
        print(f"    - Occupied: {len(slot_data['appointments']) > 0}")
        
        for apt in slot_data['appointments']:
            print(f"      * {apt.customer.username} - {apt.selected_service.name}")

if __name__ == '__main__':
    debug_slot_availability()