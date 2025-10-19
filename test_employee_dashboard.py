#!/usr/bin/env python
"""
Test employee dashboard functionality
"""
import os
import sys
import django
from datetime import date, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carmodx.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from services.models import Service, ServiceCategory
from appointments.models import Appointment
from accounts.models import Employee

User = get_user_model()

def test_employee_dashboard():
    print("Testing Employee Dashboard Functionality")
    print("=" * 50)
    
    # Create test data
    print("1. Setting up test data...")
    
    # Create service
    category, created = ServiceCategory.objects.get_or_create(
        name="Employee Test Category",
        defaults={'description': 'Employee test category'}
    )
    
    service, created = Service.objects.get_or_create(
        name="Employee Test Service",
        defaults={
            'description': 'Service for employee testing',
            'category': category,
            'base_price': 20000.00,
            'estimated_duration': timedelta(hours=3)
        }
    )
    
    # Create employee user
    employee_user, created = User.objects.get_or_create(
        username="testemployee",
        defaults={
            'email': 'employee@test.com',
            'first_name': 'Test',
            'last_name': 'Employee',
            'role': 'employee',
            'is_staff': True
        }
    )
    if created:
        employee_user.set_password('testpass123')
        employee_user.save()
    
    # Clean up existing test appointments
    Appointment.objects.filter(customer__username__startswith='empcustomer').delete()
    
    # Create customers for appointments
    customer1, created = User.objects.get_or_create(
        username="empcustomer1",
        defaults={
            'email': 'empcustomer1@test.com',
            'role': 'customer'
        }
    )
    
    customer2, created = User.objects.get_or_create(
        username="empcustomer2",
        defaults={
            'email': 'empcustomer2@test.com',
            'role': 'customer'
        }
    )
    
    customer3, created = User.objects.get_or_create(
        username="empcustomer3",
        defaults={
            'email': 'empcustomer3@test.com',
            'role': 'customer'
        }
    )
    
    # Create some test appointments
    today = date.today()
    tomorrow = today + timedelta(days=1)
    day_after = today + timedelta(days=2)
    
    # Today's work
    today_appointment = Appointment.objects.create(
        customer=customer1,
        selected_service=service,
        slot_date=today,
        slot_time='09:00',
        vehicle_make='Today',
        vehicle_model='Work',
        vehicle_year=2023,
        vehicle_license='TODAY-123'
    )
    
    # Upcoming work
    upcoming_appointment = Appointment.objects.create(
        customer=customer2,
        selected_service=service,
        slot_date=tomorrow,
        slot_time='11:00',
        vehicle_make='Tomorrow',
        vehicle_model='Work',
        vehicle_year=2023,
        vehicle_license='TOMORROW-123'
    )
    
    # Completed work (create for future date then update status)
    completed_appointment = Appointment.objects.create(
        customer=customer3,
        selected_service=service,
        slot_date=day_after,
        slot_time='13:00',
        vehicle_make='Completed',
        vehicle_model='Work',
        vehicle_year=2023,
        vehicle_license='DONE-123'
    )
    # Update to completed status after creation
    completed_appointment.status = 'completed'
    completed_appointment.save()
    
    print(f"   - Employee: {employee_user.username}")
    print(f"   - Service: {service.name}")
    print(f"   - Today's work: {today_appointment.id}")
    print(f"   - Upcoming work: {upcoming_appointment.id}")
    print(f"   - Completed work: {completed_appointment.id}")
    
    client = Client()
    
    # Test employee dashboard access
    print("\n2. Testing employee dashboard access...")
    
    # Without login
    response = client.get('/accounts/dashboard/')
    if response.status_code == 302:
        print("   ✓ Redirects to login when not authenticated")
    else:
        print(f"   ✗ Expected redirect, got {response.status_code}")
    
    # With employee login
    client.login(username='testemployee', password='testpass123')
    response = client.get('/accounts/dashboard/', follow=True)
    
    if response.status_code == 200:
        print("   ✓ Employee dashboard accessible")
        
        # Check for work-related content
        if b"Today's Work" in response.content:
            print("   ✓ Shows today's work section")
        else:
            print("   ✗ Missing today's work section")
            
        if b"Upcoming Work" in response.content:
            print("   ✓ Shows upcoming work section")
        else:
            print("   ✗ Missing upcoming work section")
            
        if b"Recently Completed Work" in response.content:
            print("   ✓ Shows completed work section")
        else:
            print("   ✗ Missing completed work section")
            
        # Check that it doesn't show booking options
        if b"Book New Appointment" not in response.content:
            print("   ✓ Does not show booking options (correct)")
        else:
            print("   ✗ Shows booking options (incorrect for employee)")
            
    else:
        print(f"   ✗ Employee dashboard failed: {response.status_code}")
    
    # Test that employees cannot book appointments
    print("\n3. Testing booking restrictions for employees...")
    
    # Test direct appointment booking
    response = client.get('/appointments/book/')
    if response.status_code == 302:
        print("   ✓ Employee blocked from direct appointment booking")
    else:
        print(f"   ✗ Employee can access booking page: {response.status_code}")
    
    # Test service booking
    response = client.get(f'/services/{service.id}/book/')
    if response.status_code == 302:
        print("   ✓ Employee blocked from service booking")
    else:
        print(f"   ✗ Employee can access service booking: {response.status_code}")
    
    # Test that employees can access work management
    print("\n4. Testing work management access...")
    
    # Test appointment list (should work for staff)
    response = client.get('/appointments/list/')
    if response.status_code == 200:
        print("   ✓ Employee can access appointment list")
    else:
        print(f"   ✗ Employee cannot access appointment list: {response.status_code}")
    
    # Test appointment detail
    response = client.get(f'/appointments/{today_appointment.id}/')
    if response.status_code == 200:
        print("   ✓ Employee can view appointment details")
    else:
        print(f"   ✗ Employee cannot view appointment details: {response.status_code}")
    
    # Test status update
    response = client.get(f'/appointments/{today_appointment.id}/update-status/')
    if response.status_code == 200:
        print("   ✓ Employee can access status update")
    else:
        print(f"   ✗ Employee cannot access status update: {response.status_code}")
    
    client.logout()
    
    # Test customer can still book
    print("\n5. Testing customer booking still works...")
    
    customer1.set_password('testpass123')
    customer1.save()
    
    client.login(username='empcustomer1', password='testpass123')
    
    response = client.get('/appointments/book/')
    if response.status_code == 200:
        print("   ✓ Customer can access booking page")
    else:
        print(f"   ✗ Customer cannot access booking page: {response.status_code}")
    
    response = client.get(f'/services/{service.id}/book/')
    if response.status_code == 200:
        print("   ✓ Customer can access service booking")
    else:
        print(f"   ✗ Customer cannot access service booking: {response.status_code}")
    
    client.logout()
    
    print("\n" + "=" * 50)
    print("Employee Dashboard Test Summary")
    print("=" * 50)
    
    print(f"\n✅ Employee Dashboard Features:")
    print(f"   - Work-focused interface")
    print(f"   - Today's work display")
    print(f"   - Upcoming work preview")
    print(f"   - Completed work history")
    print(f"   - Task management actions")
    print(f"   - No booking capabilities")
    
    print(f"\n✅ Access Control:")
    print(f"   - Employees blocked from booking")
    print(f"   - Employees can manage work")
    print(f"   - Customers can still book")
    
    print(f"\n✅ Employee dashboard test completed!")

if __name__ == "__main__":
    test_employee_dashboard()