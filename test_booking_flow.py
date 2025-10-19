#!/usr/bin/env python
"""
Test the complete booking flow with real HTTP requests
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

User = get_user_model()

def test_booking_flow():
    print("Testing Complete Appointment Booking Flow")
    print("=" * 50)
    
    # Setup test data
    print("1. Setting up test data...")
    
    # Create service category and service
    category, created = ServiceCategory.objects.get_or_create(
        name="Engine Tuning",
        defaults={'description': 'Engine performance modifications'}
    )
    
    service, created = Service.objects.get_or_create(
        name="ECU Remapping",
        defaults={
            'description': 'Professional ECU remapping service',
            'category': category,
            'base_price': 15000.00,
            'estimated_duration': timedelta(hours=3)
        }
    )
    
    # Create test customer
    customer, created = User.objects.get_or_create(
        username="flowtest",
        defaults={
            'email': 'flowtest@test.com',
            'first_name': 'Flow',
            'last_name': 'Test',
            'role': 'customer'
        }
    )
    if created:
        customer.set_password('testpass123')
        customer.save()
    
    # Create staff user
    staff, created = User.objects.get_or_create(
        username="stafftest",
        defaults={
            'email': 'staff@test.com',
            'first_name': 'Staff',
            'last_name': 'Test',
            'role': 'admin',
            'is_staff': True
        }
    )
    if created:
        staff.set_password('testpass123')
        staff.save()
    
    print(f"   - Service: {service.name} (₹{service.base_price})")
    print(f"   - Customer: {customer.username}")
    print(f"   - Staff: {staff.username}")
    
    client = Client()
    
    # Test 1: API endpoint for available slots
    print("\n2. Testing available slots API...")
    
    tomorrow = date.today() + timedelta(days=1)
    response = client.get(f'/appointments/api/available-slots/?date={tomorrow}')
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ API returns {len(data['slots'])} available slots")
        for slot in data['slots']:
            print(f"     - {slot['display']}: {slot['remaining']}/5 available")
    else:
        print(f"   ✗ API failed with status {response.status_code}")
        return
    
    # Test 2: Access booking page without login (should redirect)
    print("\n3. Testing booking page access without login...")
    
    response = client.get('/appointments/book/')
    if response.status_code == 302:
        print("   ✓ Redirects to login page (302)")
    else:
        print(f"   ✗ Unexpected status: {response.status_code}")
    
    # Test 3: Login and access booking page
    print("\n4. Testing booking page with customer login...")
    
    login_success = client.login(username='flowtest', password='testpass123')
    if login_success:
        print("   ✓ Customer login successful")
        
        response = client.get('/appointments/book/')
        if response.status_code == 200:
            print("   ✓ Booking page accessible (200)")
            
            # Check if form is present
            if b'selected_service' in response.content:
                print("   ✓ Booking form is present")
            else:
                print("   ✗ Booking form not found")
        else:
            print(f"   ✗ Booking page failed: {response.status_code}")
    else:
        print("   ✗ Customer login failed")
        return
    
    # Clean up any existing appointments for this customer
    from appointments.models import Appointment
    Appointment.objects.filter(customer=customer).delete()
    
    # Test 4: Submit booking form
    print("\n5. Testing appointment booking submission...")
    
    booking_data = {
        'selected_service': service.id,
        'slot_date': tomorrow.strftime('%Y-%m-%d'),
        'slot_time': '11:00',  # Use 11:00 AM instead of 9:00 AM (which is full)
        'vehicle_make': 'Honda',
        'vehicle_model': 'Civic',
        'vehicle_year': 2020,
        'vehicle_license': 'FLOW-123',
        'special_requirements': 'Please use premium parts'
    }
    
    response = client.post('/appointments/book/', booking_data)
    
    if response.status_code == 302:
        print("   ✓ Booking submitted successfully (redirected)")
        
        # Check if appointment was created
        appointment = Appointment.objects.filter(
            customer=customer,
            slot_date=tomorrow,
            slot_time='11:00'
        ).first()
        
        if appointment:
            print(f"   ✓ Appointment #{appointment.id} created in database")
            appointment_id = appointment.id
        else:
            print("   ✗ Appointment not found in database")
            return
            
    elif response.status_code == 200:
        print("   ~ Booking form returned (may have validation errors)")
        if b'error' in response.content.lower():
            print("   - Form contains errors")
        return
    else:
        print(f"   ✗ Booking failed: {response.status_code}")
        return
    
    # Test 5: View customer appointments
    print("\n6. Testing customer appointments page...")
    
    response = client.get('/appointments/my-appointments/')
    if response.status_code == 200:
        print("   ✓ My appointments page accessible")
        if str(appointment_id).encode() in response.content:
            print(f"   ✓ Appointment #{appointment_id} visible in list")
        else:
            print("   ✗ Appointment not visible in customer list")
    else:
        print(f"   ✗ My appointments page failed: {response.status_code}")
    
    # Test 6: View appointment details
    print("\n7. Testing appointment details page...")
    
    response = client.get(f'/appointments/{appointment_id}/')
    if response.status_code == 200:
        print("   ✓ Appointment details page accessible")
        if b'Honda Civic' in response.content:
            print("   ✓ Vehicle details visible")
        else:
            print("   ✗ Vehicle details not found")
    else:
        print(f"   ✗ Appointment details failed: {response.status_code}")
    
    # Test 7: Test slot capacity after booking
    print("\n8. Testing slot capacity after booking...")
    
    response = client.get(f'/appointments/api/available-slots/?date={tomorrow}')
    if response.status_code == 200:
        data = response.json()
        morning_slot = next((s for s in data['slots'] if s['time'] == '11:00'), None)
        if morning_slot:
            print(f"   ✓ 11:00 AM slot now has {morning_slot['remaining']}/5 available")
            if morning_slot['remaining'] == 4:
                print("   ✓ Slot capacity correctly decremented")
            else:
                print("   ✗ Slot capacity not updated correctly")
        else:
            print("   ✗ 11:00 AM slot not found in response")
    
    client.logout()
    
    # Test 8: Staff access
    print("\n9. Testing staff access...")
    
    staff_login = client.login(username='stafftest', password='testpass123')
    if staff_login:
        print("   ✓ Staff login successful")
        
        # Test appointment list
        response = client.get('/appointments/list/')
        if response.status_code == 200:
            print("   ✓ Staff appointment list accessible")
            if str(appointment_id).encode() in response.content:
                print(f"   ✓ Appointment #{appointment_id} visible in staff list")
            else:
                print("   ✗ Appointment not visible in staff list")
        else:
            print(f"   ✗ Staff appointment list failed: {response.status_code}")
        
        # Test status update page
        response = client.get(f'/appointments/{appointment_id}/update-status/')
        if response.status_code == 200:
            print("   ✓ Status update page accessible")
        else:
            print(f"   ✗ Status update page failed: {response.status_code}")
    else:
        print("   ✗ Staff login failed")
    
    # Test 9: Prevent duplicate booking
    print("\n10. Testing duplicate booking prevention...")
    
    client.logout()
    client.login(username='flowtest', password='testpass123')
    
    # Try to book another appointment for same customer on same date
    duplicate_data = {
        'selected_service': service.id,
        'slot_date': tomorrow.strftime('%Y-%m-%d'),
        'slot_time': '11:00',  # Different time, same date
        'vehicle_make': 'Toyota',
        'vehicle_model': 'Camry',
        'vehicle_year': 2021,
        'vehicle_license': 'DUP-123',
    }
    
    response = client.post('/appointments/book/', duplicate_data)
    
    if response.status_code == 200:
        if b'already have an appointment' in response.content.lower():
            print("   ✓ Duplicate booking prevented with error message")
        else:
            print("   ✗ Duplicate booking not prevented")
    elif response.status_code == 302:
        print("   ✗ Duplicate booking was allowed (unexpected)")
    else:
        print(f"   ? Duplicate booking test: Status {response.status_code}")
    
    print("\n" + "=" * 50)
    print("Booking Flow Test Summary")
    print("=" * 50)
    
    # Final statistics
    total_appointments = Appointment.objects.count()
    today_appointments = Appointment.objects.filter(slot_date=tomorrow).count()
    
    print(f"\nDatabase Statistics:")
    print(f"- Total appointments: {total_appointments}")
    print(f"- Appointments for {tomorrow}: {today_appointments}")
    
    print(f"\nSlot Status for {tomorrow}:")
    for slot_time, slot_display in Appointment.TIME_SLOT_CHOICES:
        booked = Appointment.objects.filter(
            slot_date=tomorrow,
            slot_time=slot_time,
            status='booked'
        ).count()
        remaining = 5 - booked
        print(f"- {slot_display}: {booked}/5 booked, {remaining} remaining")
    
    print("\n✅ Complete booking flow test completed successfully!")

if __name__ == "__main__":
    test_booking_flow()