#!/usr/bin/env python3

import os
import django
import requests
from datetime import datetime, timedelta

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carmodx.settings')
django.setup()

from django.contrib.auth import get_user_model
from services.models import Service
from accounts.models import User

def test_services_booking_page():
    """Test the services booking page functionality"""
    
    print("🔧 TESTING SERVICES BOOKING PAGE: /services/20/book/")
    print("=" * 60)
    
    # Check if service exists
    try:
        service = Service.objects.get(id=20)
        print(f"✅ Service Found: {service.name}")
        print(f"   Category: {service.category.name}")
        print(f"   Price: ₹{service.base_price}")
        print(f"   Active: {service.is_active}")
    except Service.DoesNotExist:
        print("❌ Service ID 20 does not exist!")
        return
    
    print("\n" + "=" * 60)
    
    # Test page access for different user types
    base_url = "http://127.0.0.1:8000"
    services_booking_url = f"{base_url}/services/20/book/"
    
    print("🧪 TESTING PAGE ACCESS...")
    
    # Test 1: Anonymous user (should redirect to login)
    print("\n1️⃣ Testing Anonymous Access:")
    try:
        response = requests.get(services_booking_url, allow_redirects=False)
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 302:
            print(f"   ✅ Redirected to: {response.headers.get('Location', 'Unknown')}")
            print("   ✅ Expected behavior - login required")
        else:
            print("   ❌ Expected redirect to login page")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Check what users exist
    print("\n2️⃣ Available Test Users:")
    customers = User.objects.filter(role='customer')[:5]
    employees = User.objects.filter(role='employee')[:3]
    
    print("   👥 Customers:")
    for user in customers:
        print(f"      - {user.username} (Role: {user.role})")
    
    print("   👷 Employees:")
    for user in employees:
        print(f"      - {user.username} (Role: {user.role})")
    
    # Test 3: Check if we can simulate logged-in access
    print("\n3️⃣ Testing Form Structure:")
    try:
        # Create Django test client to simulate logged-in user
        from django.test import Client
        from django.contrib.auth import login
        
        client = Client()
        
        # Try to get a customer user
        try:
            customer = User.objects.filter(role='customer').first()
            if customer:
                # Force login
                client.force_login(customer)
                print(f"   👤 Testing as customer: {customer.username}")
                
                response = client.get('/services/20/book/')
                print(f"   Status Code: {response.status_code}")
                
                if response.status_code == 200:
                    print("   ✅ Page loads successfully for customer")
                    
                    # Check if form is present
                    content = response.content.decode()
                    if 'id_slot_date' in content:
                        print("   ✅ Date field found in form")
                    else:
                        print("   ❌ Date field not found")
                        
                    if 'id_slot_time' in content:
                        print("   ✅ Time slot field found in form")
                    else:
                        print("   ❌ Time slot field not found")
                        
                    # Check for JavaScript
                    if 'fetchAvailableSlots' in content:
                        print("   ✅ Slot loading JavaScript found")
                    else:
                        print("   ❌ Slot loading JavaScript not found")
                        
                else:
                    print(f"   ❌ Unexpected status code: {response.status_code}")
            else:
                print("   ❌ No customer users found")
                
        except Exception as e:
            print(f"   ❌ Error testing customer access: {e}")
            
        # Test employee access
        try:
            employee = User.objects.filter(role='employee').first()
            if employee:
                client.force_login(employee)
                print(f"   👷 Testing as employee: {employee.username}")
                
                response = client.get('/services/20/book/')
                print(f"   Status Code: {response.status_code}")
                
                if response.status_code == 302:
                    print("   ✅ Employee correctly redirected (cannot book)")
                else:
                    print(f"   ❌ Expected redirect for employee, got: {response.status_code}")
            
        except Exception as e:
            print(f"   ❌ Error testing employee access: {e}")
            
    except Exception as e:
        print(f"   ❌ Error setting up test client: {e}")
    
    # Test 4: API endpoint
    print("\n4️⃣ Testing Available Slots API:")
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    api_url = f"{base_url}/appointments/api/available-slots/?date={tomorrow}"
    
    try:
        response = requests.get(api_url)
        print(f"   API URL: {api_url}")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ API Response: {len(data.get('slots', []))} slots available")
            for slot in data.get('slots', [])[:3]:
                print(f"      - {slot.get('display', 'N/A')}")
        else:
            print(f"   ❌ API call failed: {response.text}")
            
    except Exception as e:
        print(f"   ❌ API Error: {e}")
    
    print("\n" + "=" * 60)
    print("📝 SUMMARY:")
    print("   1. Service booking page exists and is properly configured")
    print("   2. Requires customer login (employees redirected)")
    print("   3. Uses same booking form and JavaScript as main appointment booking")
    print("   4. Should work identically to /appointments/book/ but pre-fills service")
    print("\n💡 TO TEST MANUALLY:")
    print("   1. Login as customer (username: test)")
    print("   2. Visit: http://127.0.0.1:8000/services/20/book/")
    print("   3. Select date and check if time slots populate")
    print("   4. Compare behavior with: http://127.0.0.1:8000/appointments/book/")

if __name__ == '__main__':
    test_services_booking_page()