#!/usr/bin/env python3

"""
Test the update button functionality on appointment detail pages
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
from appointments.models import Appointment
from services.models import Service
from datetime import date, timedelta

def test_update_button():
    """Test that the update button appears and works correctly"""
    
    print("🔧 Testing Update Button on Appointment Detail Page")
    print("=" * 55)
    
    client = Client()
    User = get_user_model()
    
    # Get or create employee user
    try:
        employee = User.objects.filter(role='employee').first()
        if not employee:
            employee = User.objects.create_user(
                username='updatetest_emp',
                email='updatetest@emp.com',
                password='emp123',
                role='employee',
                first_name='Update',
                last_name='Tester'
            )
            print(f"✅ Created employee user: {employee.username}")
        else:
            print(f"✅ Using employee user: {employee.username}")
    except Exception as e:
        print(f"❌ Error with employee user: {e}")
        return

    # Get customer and create test appointment
    try:
        customer = User.objects.get(username='slottest')
        print(f"✅ Using customer: {customer.username}")
    except User.DoesNotExist:
        print("❌ slottest user not found")
        return

    # Create test appointment
    service = Service.objects.filter(is_active=True).first()
    tomorrow = date.today() + timedelta(days=1)
    
    appointment = Appointment.objects.create(
        customer=customer,
        selected_service=service,
        slot_date=tomorrow,
        slot_time='09:00',
        vehicle_make='Toyota',
        vehicle_model='Camry',
        vehicle_year=2020,
        vehicle_license='UPDATE-TEST',
        status='booked'
    )
    
    print(f"✅ Created test appointment: #{appointment.id}")
    
    # Test 1: Access detail page as customer (should not see update button)
    print(f"\n👤 Test 1: Customer access")
    customer_login = client.login(username='slottest', password='slot123')
    if customer_login:
        detail_url = reverse('appointments:appointment_detail', kwargs={'appointment_id': appointment.id})
        response = client.get(detail_url)
        
        print(f"   Detail URL: {detail_url}")
        print(f"   Page status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.content.decode()
            has_update_button = 'Update Status & Work' in content
            print(f"   Update button visible: {has_update_button} (should be False)")
        
        client.logout()
    else:
        print("   ❌ Customer login failed")
    
    # Test 2: Access detail page as employee (should see update button)
    print(f"\n🔧 Test 2: Employee access")
    
    # Set employee password
    employee.set_password('emp123')
    employee.save()
    
    employee_login = client.login(username=employee.username, password='emp123')
    if employee_login:
        response = client.get(detail_url)
        
        print(f"   Employee login: ✅")
        print(f"   Page status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.content.decode()
            
            # Check for update button and quick actions
            checks = [
                ('Update Status & Work button', 'Update Status & Work' in content),
                ('Assign to Me button', 'Assign to Me' in content),
                ('Update URL link', f'/appointments/{appointment.id}/update-status/' in content),
                ('Quick action forms', 'action" value="assign_self"' in content)
            ]
            
            print(f"   Employee features:")
            for check_name, check_result in checks:
                status = "✅" if check_result else "❌"
                print(f"     {status} {check_name}")
    else:
        print("   ❌ Employee login failed")
    
    # Test 3: Test direct access to update page
    print(f"\n📝 Test 3: Direct access to update page")
    update_url = reverse('appointments:update_status', kwargs={'appointment_id': appointment.id})
    update_response = client.get(update_url)
    
    print(f"   Update URL: {update_url}")
    print(f"   Update page status: {update_response.status_code}")
    
    if update_response.status_code == 200:
        print("   ✅ Update page accessible")
    elif update_response.status_code == 302:
        print("   ⚠️  Redirected (might be permission issue)")
    
    # Cleanup
    appointment.delete()
    print(f"\n🧹 Test appointment #{appointment.id} cleaned up")
    
    print(f"\n💡 Manual Test:")
    print(f"1. Login as employee: {employee.username} / emp123")
    print(f"2. Go to any appointment detail page")
    print(f"3. Look for 'Update Status & Work' button")
    print(f"4. Click it to go to update page")

if __name__ == '__main__':
    test_update_button()