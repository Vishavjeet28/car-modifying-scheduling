#!/usr/bin/env python3

import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carmodx.settings')
django.setup()

from django.test import Client
from accounts.models import User

def test_services_booking_dropdown():
    """Quick test of services booking page dropdown functionality"""
    
    print("🔧 TESTING SERVICES BOOKING PAGE: /services/20/book/")
    print("=" * 60)
    
    # Get customer user
    customer = User.objects.filter(role='customer').first()
    if not customer:
        print("❌ No customer users found!")
        return
        
    print(f"👤 Testing as customer: {customer.username}")
    
    # Test the page
    client = Client()
    client.force_login(customer)
    
    response = client.get('/services/20/book/')
    print(f"📄 Page Status: {response.status_code}")
    
    if response.status_code == 200:
        content = response.content.decode()
        
        # Check key elements
        checks = [
            ('Premium Audio Setup', 'Service name displayed'),
            ('id_slot_date', 'Date field present'),
            ('id_slot_time', 'Time field present'),
            ('fetchAvailableSlots', 'JavaScript function present'),
            ('csrf_token', 'CSRF protection present'),
            ('form method="post"', 'Form submission ready')
        ]
        
        print("\n🔍 Content Checks:")
        for check_text, description in checks:
            if check_text in content:
                print(f"   ✅ {description}")
            else:
                print(f"   ❌ {description}")
        
        # Test API endpoint directly
        print("\n🔌 Testing Available Slots API:")
        from datetime import datetime, timedelta
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        
        api_response = client.get(f'/appointments/api/available-slots/?date={tomorrow}')
        print(f"   API Status: {api_response.status_code}")
        
        if api_response.status_code == 200:
            import json
            data = json.loads(api_response.content.decode())
            slots = data.get('slots', [])
            print(f"   ✅ {len(slots)} slots available for {tomorrow}")
            for i, slot in enumerate(slots[:3]):
                print(f"      {i+1}. {slot.get('display', 'N/A')} - {slot.get('remaining', 0)} remaining")
        else:
            print(f"   ❌ API failed: {api_response.content.decode()}")
    
    print("\n" + "=" * 60)
    print("💡 MANUAL TESTING STEPS:")
    print("1. Open browser and login as customer")
    print("   - Username: test")
    print("   - Password: (try testpass123 or similar)")
    print("2. Visit: http://127.0.0.1:8000/services/20/book/")
    print("3. Select tomorrow's date")
    print("4. Check if time slots appear in dropdown")
    print("5. Compare with: http://127.0.0.1:8000/appointments/book/")
    
    print("\n✨ EXPECTED BEHAVIOR:")
    print("- Page loads with Premium Audio Setup service pre-selected")
    print("- Date selection triggers slot loading via JavaScript")
    print("- Only available time slots should appear")
    print("- Should work identically to main booking page")

if __name__ == '__main__':
    test_services_booking_dropdown()