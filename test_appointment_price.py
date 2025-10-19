#!/usr/bin/env python
"""
Test appointment price display
"""
import os
import sys
import django
from datetime import date, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carmodx.settings')
django.setup()

from django.contrib.auth import get_user_model
from services.models import Service, ServiceCategory
from appointments.models import Appointment

User = get_user_model()

def test_appointment_price():
    print("Testing Appointment Price Display")
    print("=" * 40)
    
    # Get an existing appointment or create one
    appointment = Appointment.objects.first()
    
    if appointment:
        print(f"Testing with existing appointment #{appointment.id}")
    else:
        print("Creating test appointment...")
        
        # Create test data
        category, created = ServiceCategory.objects.get_or_create(
            name="Price Test Category",
            defaults={'description': 'Price test category'}
        )
        
        service, created = Service.objects.get_or_create(
            name="Price Test Service",
            defaults={
                'description': 'Price test service',
                'category': category,
                'base_price': 25000.00,
                'estimated_duration': timedelta(hours=2)
            }
        )
        
        customer, created = User.objects.get_or_create(
            username="pricetest",
            defaults={
                'email': 'price@test.com',
                'role': 'customer'
            }
        )
        
        appointment = Appointment.objects.create(
            customer=customer,
            selected_service=service,
            slot_date=date.today() + timedelta(days=1),
            slot_time='11:00',
            vehicle_make='Price',
            vehicle_model='Test',
            vehicle_year=2023,
            vehicle_license='PRICE-123'
        )
        print(f"Created test appointment #{appointment.id}")
    
    print(f"\nAppointment Details:")
    print(f"- ID: #{appointment.id}")
    print(f"- Customer: {appointment.customer.username}")
    print(f"- Service: {appointment.selected_service.name}")
    print(f"- Service Base Price: ₹{appointment.selected_service.base_price}")
    print(f"- Service Category: {appointment.selected_service.category.name}")
    print(f"- Date: {appointment.slot_date}")
    print(f"- Time: {appointment.get_slot_time_display()}")
    print(f"- Status: {appointment.get_status_display()}")
    
    # Test template context
    print(f"\nTemplate Context Test:")
    print(f"- appointment.selected_service: {appointment.selected_service}")
    print(f"- appointment.selected_service.base_price: {appointment.selected_service.base_price}")
    print(f"- appointment.selected_service.base_price type: {type(appointment.selected_service.base_price)}")
    
    # Test if service has all required fields
    service = appointment.selected_service
    print(f"\nService Object Details:")
    print(f"- Service ID: {service.id}")
    print(f"- Service Name: {service.name}")
    print(f"- Service Description: {service.description}")
    print(f"- Service Base Price: {service.base_price}")
    print(f"- Service Category: {service.category}")
    print(f"- Service Duration: {service.estimated_duration}")
    print(f"- Service Active: {service.is_active}")
    
    # Check if duration_hours property works
    try:
        duration_hours = service.duration_hours
        print(f"- Service Duration Hours: {duration_hours}")
    except Exception as e:
        print(f"- Service Duration Hours Error: {e}")
    
    print(f"\n✅ Price test completed!")

if __name__ == "__main__":
    test_appointment_price()