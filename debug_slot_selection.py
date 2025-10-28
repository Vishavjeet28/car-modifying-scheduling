#!/usr/bin/env python3

"""
Quick test to debug the slot selection issue
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
from datetime import date, timedelta
import json

def test_slot_selection_debug():
    """Debug the slot selection issue"""
    
    print("🔍 Debugging Slot Selection Issue")
    print("=" * 40)
    
    client = Client()
    User = get_user_model()
    
    # Test API endpoint directly
    tomorrow = date.today() + timedelta(days=1)
    api_url = reverse('appointments:available_slots_api')
    
    print(f"📡 Testing API: {api_url}?date={tomorrow}")
    response = client.get(api_url, {'date': tomorrow.isoformat()})
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = json.loads(response.content)
        print(f"Response data structure:")
        print(f"  - slots: {len(data.get('slots', []))} items")
        print(f"  - all_slots: {len(data.get('all_slots', []))} items")
        print(f"  - total_slots: {data.get('total_slots')}")
        
        print(f"\nAvailable slots:")
        for slot in data.get('slots', []):
            print(f"  - {slot}")
        
        print(f"\nAll slots:")
        for slot in data.get('all_slots', []):
            print(f"  - {slot}")
    
    # Test service booking page
    print(f"\n🏪 Testing Service Booking Page")
    services = Service.objects.filter(is_active=True)[:1]
    if services:
        service = services[0]
        booking_url = reverse('services:book_service', kwargs={'service_id': service.id})
        print(f"Service URL: {booking_url}")
        
        response = client.get(booking_url)
        print(f"Booking page status: {response.status_code}")
        
        if response.status_code == 302:
            print("⚠️  Redirected (probably to login page)")
        elif response.status_code == 200:
            content = response.content.decode()
            
            # Check for key elements
            checks = [
                ('id_slot_date field', 'id="id_slot_date"' in content),
                ('id_slot_time field', 'id="id_slot_time"' in content),
                ('booking-form', 'id="booking-form"' in content),
                ('book-btn', 'id="book-btn"' in content),
                ('slot-container', 'id="slot-container"' in content),
                ('slots-grid', 'id="slots-grid"' in content),
                ('JavaScript functions', 'fetchAvailableSlots' in content),
                ('API URL in JS', 'available_slots_api' in content)
            ]
            
            print(f"\nHTML Elements Check:")
            for check_name, check_result in checks:
                status = "✅" if check_result else "❌"
                print(f"  {status} {check_name}")
    
    print(f"\n💡 Debugging Tips:")
    print(f"1. Open browser console on {booking_url}")
    print(f"2. Select a date to trigger slot loading")
    print(f"3. Watch console logs for debugging info")
    print(f"4. Check if slot cards are created with click events")
    print(f"5. Verify selectedSlot variable is set when clicking")

if __name__ == '__main__':
    test_slot_selection_debug()