#!/usr/bin/env python3

import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carmodx.settings')
django.setup()

from django.test import Client
from accounts.models import User

def test_dropdown_fix():
    """Test if the dropdown fix is working"""
    
    print("🔧 TESTING DROPDOWN FIX")
    print("=" * 50)
    
    # Get customer user
    customer = User.objects.filter(role='customer').first()
    if not customer:
        print("❌ No customer users found!")
        return
        
    print(f"👤 Testing as customer: {customer.username}")
    
    client = Client()
    client.force_login(customer)
    
    # Test booking page
    response = client.get('/appointments/book/')
    print(f"📄 Page Status: {response.status_code}")
    
    if response.status_code == 200:
        content = response.content.decode()
        
        # Check for the essential elements
        checks = [
            ('id="id_slot_date"', 'Date field with correct ID'),
            ('id="id_slot_time"', 'Time field with correct ID'),
            ('loadAvailableSlots()', 'JavaScript function'),
            ('🚀 Page loaded, setting up', 'Debug logging added'),
            ('Date input found:', 'Element detection logging'),
            ('Time select found:', 'Element detection logging')
        ]
        
        print("\n🔍 Page Content Checks:")
        for check_text, description in checks:
            if check_text in content:
                print(f"   ✅ {description}")
            else:
                print(f"   ❌ {description}")
        
        # Check if IDs are actually rendered correctly
        if 'id="id_slot_date"' in content and 'id="id_slot_time"' in content:
            print("\n🎉 SUCCESS: Form field IDs are now correct!")
            print("   The dropdown should now work when you:")
            print("   1. Login as customer")
            print("   2. Visit: http://127.0.0.1:8001/appointments/book/")
            print("   3. Select a date")
            print("   4. Watch time slots populate in dropdown")
        else:
            print("\n❌ Form field IDs still not correct")
    
    # Also test services booking page
    print(f"\n📄 Testing services booking page...")
    response = client.get('/services/20/book/')
    print(f"Services page status: {response.status_code}")
    
    if response.status_code == 200:
        content = response.content.decode()
        if 'id="id_slot_date"' in content and 'id="id_slot_time"' in content:
            print("   ✅ Services booking page also fixed!")
        else:
            print("   ❌ Services booking page still has issues")

if __name__ == '__main__':
    test_dropdown_fix()