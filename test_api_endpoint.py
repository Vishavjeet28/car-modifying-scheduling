#!/usr/bin/env python
"""
Test the API endpoint directly to see the response
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
from django.urls import reverse
import json

def test_api_endpoint():
    print("🔍 Testing Available Slots API Endpoint")
    print("=" * 60)
    
    client = Client()
    
    # Test for tomorrow (which has some appointments)
    tomorrow = date.today() + timedelta(days=1)
    
    url = reverse('appointments:available_slots_api')
    response = client.get(url, {'date': tomorrow.isoformat()})
    
    print(f"API URL: {url}")
    print(f"Test date: {tomorrow}")
    print(f"Response status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n=== API Response ===")
        print(f"Available slots for dropdown: {len(data['slots'])}")
        
        print(f"\nDropdown slots (what users can select):")
        for slot in data['slots']:
            print(f"  - {slot['time']} ({slot['display']}) - {slot['remaining']} slots remaining")
        
        print(f"\nAll slots (display information):")
        for slot in data['all_slots']:
            status = "OCCUPIED" if slot['occupied'] else "AVAILABLE"
            appointments_info = ""
            if slot['appointments']:
                appointments_info = f" - {slot['appointments'][0]['service']}"
            print(f"  - {slot['time']} ({slot['display']}): {status}{appointments_info}")
        
        print(f"\nDaily capacity:")
        print(f"  - Total: {data['daily_capacity']['total']}")
        print(f"  - Occupied: {data['daily_capacity']['occupied']}")
        print(f"  - Remaining: {data['daily_capacity']['remaining']}")
        
        print(f"\nCapacity info: {data['capacity_info']}")
        
        # Test for a date with 5 appointments (should return no available slots)
        print(f"\n" + "=" * 60)
        print(f"Testing date with full capacity (2025-10-20):")
        
        full_date = date(2025, 10, 20)  # This date has 5 appointments from our test
        response = client.get(url, {'date': full_date.isoformat()})
        
        if response.status_code == 200:
            data = response.json()
            print(f"Available slots for dropdown: {len(data['slots'])}")
            print(f"Daily remaining: {data['daily_capacity']['remaining']}")
            
            if len(data['slots']) == 0:
                print("✅ Correctly shows no available slots for fully booked date")
            else:
                print("❌ Still showing available slots for fully booked date!")
                for slot in data['slots']:
                    print(f"  - {slot['time']} ({slot['display']})")
        
    else:
        print(f"❌ API Error: {response.status_code}")
        print(response.content.decode())

if __name__ == '__main__':
    test_api_endpoint()