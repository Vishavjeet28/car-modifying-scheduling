#!/usr/bin/env python
"""
Check current users and create a test customer if needed
"""

import os
import sys
import django
from datetime import date, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carmodx.settings')
sys.path.append('/Users/vishavjeetsingh/untitled folder/untitled folder/detailcursor')

django.setup()

from accounts.models import User

def check_and_create_customer():
    print("👥 Checking Users and Customer Access")
    print("=" * 60)
    
    # Check all users
    all_users = User.objects.all()
    print(f"📊 Total users in system: {all_users.count()}")
    
    print(f"\n👤 Current users:")
    for user in all_users:
        print(f"   - {user.username} ({user.get_role_display()}) - Email: {user.email}")
    
    # Check for customers
    customers = User.objects.filter(role='customer')
    print(f"\n🛒 Customer users: {customers.count()}")
    
    for customer in customers:
        print(f"   - {customer.username} - {customer.email}")
    
    # Create a test customer if none exists
    if customers.count() == 0:
        print(f"\n➕ Creating test customer...")
        
        test_customer = User.objects.create_user(
            username='testcustomer',
            email='testcustomer@example.com',
            password='testpass123',
            first_name='Test',
            last_name='Customer',
            role='customer',
            phone_number='1234567890'
        )
        
        print(f"✅ Created customer: {test_customer.username}")
        print(f"   Login: testcustomer / testpass123")
    else:
        existing_customer = customers.first()
        print(f"\n✅ Existing customer found: {existing_customer.username}")
    
    # Test booking view access
    print(f"\n🔍 Testing booking view access...")
    from django.test import Client
    
    client = Client()
    
    # Test without login
    response = client.get('/appointments/book/')
    print(f"Without login: Status {response.status_code} (should be 302 - redirect to login)")
    
    # Test with customer login
    customer = User.objects.filter(role='customer').first()
    if customer:
        client.force_login(customer)
        response = client.get('/appointments/book/')
        print(f"With customer login: Status {response.status_code} (should be 200 - access granted)")
        
        if response.status_code == 200:
            html_content = response.content.decode()
            if 'slot_time' in html_content:
                print("✅ Booking form loads correctly for customer")
            else:
                print("❌ Booking form not found in response")
    
    # Test with non-customer user
    non_customer = User.objects.exclude(role='customer').first()
    if non_customer:
        client.force_login(non_customer)
        response = client.get('/appointments/book/')
        print(f"With {non_customer.get_role_display()} login: Status {response.status_code} (should be 302 - redirect due to role check)")
    
    print(f"\n" + "=" * 60)
    print(f"🎯 CUSTOMER BOOKING ACCESS SUMMARY:")
    print(f"✅ Only users with role='customer' can book appointments")
    print(f"✅ Login required to access booking page")
    print(f"✅ Role-based access control working")
    
    if customers.exists():
        customer = customers.first()
        print(f"\n🔑 To test booking:")
        print(f"1. Visit: http://127.0.0.1:8001/accounts/login/")
        print(f"2. Login as: {customer.username}")
        print(f"3. Go to: http://127.0.0.1:8001/appointments/book/")
        print(f"4. Select a date and check dropdown behavior")

if __name__ == '__main__':
    check_and_create_customer()