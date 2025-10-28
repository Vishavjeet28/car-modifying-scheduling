#!/usr/bin/env python3

import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carmodx.settings')
django.setup()

from django.test import Client
from accounts.models import User
from datetime import datetime, timedelta
import json

def debug_dropdown_issue():
    """Debug why time slots are not showing after selecting date"""
    
    print("🔧 DEBUGGING DROPDOWN ISSUE")
    print("=" * 60)
    
    # Get customer user
    customer = User.objects.filter(role='customer').first()
    if not customer:
        print("❌ No customer users found!")
        return
        
    print(f"👤 Testing as customer: {customer.username}")
    
    client = Client()
    client.force_login(customer)
    
    # Test 1: Check if booking page loads
    print("\n1️⃣ CHECKING BOOKING PAGE:")
    response = client.get('/appointments/book/')
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        content = response.content.decode()
        
        # Check essential elements
        elements = {
            'id_slot_date': 'Date input field',
            'id_slot_time': 'Time select field', 
            'loadAvailableSlots': 'JavaScript function',
            'available_slots_api': 'API URL reference'
        }
        
        for element, description in elements.items():
            if element in content:
                print(f"   ✅ {description} found")
            else:
                print(f"   ❌ {description} missing")
    
    # Test 2: Check API endpoint directly
    print("\n2️⃣ TESTING API ENDPOINT:")
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    today = datetime.now().strftime('%Y-%m-%d')
    
    for date_str, label in [(today, 'today'), (tomorrow, 'tomorrow')]:
        print(f"\n   📅 Testing {label} ({date_str}):")
        
        response = client.get(f'/appointments/api/available-slots/?date={date_str}')
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = json.loads(response.content.decode())
                slots = data.get('slots', [])
                print(f"   ✅ API working: {len(slots)} slots available")
                
                if slots:
                    print("   📋 Available slots:")
                    for i, slot in enumerate(slots[:3]):
                        print(f"      {i+1}. {slot.get('display', 'N/A')} - {slot.get('remaining', 0)} remaining")
                else:
                    print("   ⚠️  No slots available for this date")
                    
                # Check daily capacity
                if 'daily_capacity' in data:
                    capacity = data['daily_capacity']
                    print(f"   📊 Daily capacity: {capacity.get('remaining', 0)}/{capacity.get('total', 0)}")
                    
            except json.JSONDecodeError as e:
                print(f"   ❌ Invalid JSON response: {e}")
                print(f"   Raw response: {response.content.decode()[:100]}")
        else:
            print(f"   ❌ API failed with status {response.status_code}")
            print(f"   Response: {response.content.decode()[:100]}")
    
    # Test 3: Check form field ID consistency  
    print("\n3️⃣ CHECKING FORM FIELD IDS:")
    from appointments.forms import AppointmentBookingForm
    
    form = AppointmentBookingForm()
    
    # Check if form field IDs match what JavaScript expects
    expected_ids = ['id_slot_date', 'id_slot_time']
    
    for field_id in expected_ids:
        if hasattr(form, field_id.replace('id_', '')):
            field = getattr(form, field_id.replace('id_', ''))
            actual_id = field.widget.attrs.get('id', field_id)
            print(f"   ✅ {field_id} -> actual ID: {actual_id}")
        else:
            print(f"   ❌ {field_id} field not found in form")
    
    # Test 4: Simple JavaScript debugging
    print("\n4️⃣ JAVASCRIPT DEBUGGING RECOMMENDATIONS:")
    print("   1. Open browser developer tools (F12)")
    print("   2. Go to Console tab")
    print("   3. Login as customer and visit booking page")
    print("   4. Select a date and watch for console messages:")
    print("      - '🔍 loadAvailableSlots() called'")
    print("      - '📅 Selected date: YYYY-MM-DD'")
    print("      - '📡 API Response status: 200'")
    print("      - '✅ Found X available slots'")
    
    print("\n💡 COMMON ISSUES TO CHECK:")
    print("   1. JavaScript errors preventing function execution")
    print("   2. CSRF token issues with API calls")
    print("   3. Form field ID mismatches") 
    print("   4. Date format incompatibility")
    print("   5. API returning empty slots array")
    
    print("\n🔧 IMMEDIATE FIXES TO TRY:")
    print("   1. Clear browser cache")
    print("   2. Check browser console for errors")
    print("   3. Test with different browsers")
    print("   4. Verify you're logged in as customer (not employee)")

if __name__ == '__main__':
    debug_dropdown_issue()