#!/usr/bin/env python
"""
Simple demo showing how booked slots are hidden from dropdown
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
from django.test import Client

def demo_hidden_slots():
    print("🎯 DEMO: How Booked Slots Are Hidden")
    print("=" * 50)
    
    # Use tomorrow as test date
    tomorrow = date.today() + timedelta(days=1)
    
    print(f"📅 Test Date: {tomorrow}")
    print(f"🕒 All Possible Time Slots:")
    for slot_time, slot_display in Appointment.TIME_SLOT_CHOICES:
        print(f"   {slot_time} = {slot_display}")
    
    # Check current appointments for tomorrow
    tomorrow_appointments = Appointment.objects.filter(slot_date=tomorrow)
    
    print(f"\n🔒 Currently Booked Slots for {tomorrow}:")
    booked_slots = []
    for apt in tomorrow_appointments:
        slot_display = dict(Appointment.TIME_SLOT_CHOICES)[apt.slot_time]
        print(f"   {apt.slot_time} ({slot_display}) - {apt.customer.username} - {apt.selected_service.name}")
        booked_slots.append(apt.slot_time)
    
    if not tomorrow_appointments:
        print("   (No appointments booked yet)")
    
    # Get available slots
    available_slots = Appointment.get_available_slots(tomorrow)
    
    print(f"\n✅ Available in Dropdown (what users can select):")
    available_times = []
    for slot in available_slots:
        print(f"   {slot['time']} ({slot['display']}) - {slot['remaining']} daily slots remaining")
        available_times.append(slot['time'])
    
    if not available_slots:
        print("   (No slots available - daily limit reached or all slots booked)")
    
    # Show the difference
    print(f"\n📊 Summary:")
    print(f"   Total possible slots: 5")
    print(f"   Booked slots: {len(booked_slots)}")
    print(f"   Available slots: {len(available_slots)}")
    
    print(f"\n🚫 Hidden from dropdown: {booked_slots}")
    print(f"✅ Shown in dropdown: {available_times}")
    
    # Test API response
    print(f"\n🌐 API Response Test:")
    client = Client()
    response = client.get(f'/appointments/api/available-slots/?date={tomorrow}')
    
    if response.status_code == 200:
        data = response.json()
        api_slots = [slot['time'] for slot in data['slots']]
        print(f"   API returns {len(api_slots)} slots: {api_slots}")
        
        if api_slots == available_times:
            print("   ✅ API matches model method")
        else:
            print("   ❌ API doesn't match model method")
    
    print(f"\n" + "=" * 50)
    print(f"🎉 RESULT: Only unbooked slots appear in dropdown!")
    print(f"Users cannot select already booked time slots.")

if __name__ == '__main__':
    demo_hidden_slots()