#!/usr/bin/env python
"""
Test price display in templates
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

def test_price_display():
    print("Testing Price Display in Templates")
    print("=" * 40)
    
    # Create test data with a clear price
    category, created = ServiceCategory.objects.get_or_create(
        name="Price Display Test",
        defaults={'description': 'Price display test category'}
    )
    
    service, created = Service.objects.get_or_create(
        name="Price Display Service",
        defaults={
            'description': 'Service for testing price display',
            'category': category,
            'base_price': 15000.00,  # Clear price: ₹15,000
            'estimated_duration': timedelta(hours=2)
        }
    )
    
    customer, created = User.objects.get_or_create(
        username="pricedisplay",
        defaults={
            'email': 'pricedisplay@test.com',
            'role': 'customer'
        }
    )
    if created:
        customer.set_password('testpass123')
        customer.save()
    
    # Create appointment
    appointment, created = Appointment.objects.get_or_create(
        customer=customer,
        selected_service=service,
        slot_date=date.today() + timedelta(days=1),
        slot_time='13:00',
        defaults={
            'vehicle_make': 'Price',
            'vehicle_model': 'Display',
            'vehicle_year': 2023,
            'vehicle_license': 'PRICE-456'
        }
    )
    
    print(f"Created/Found appointment #{appointment.id}")
    print(f"Service: {service.name}")
    print(f"Service Price: ₹{service.base_price}")
    
    client = Client()
    client.login(username='pricedisplay', password='testpass123')
    
    # Test My Appointments page
    print(f"\n1. Testing My Appointments page...")
    response = client.get('/appointments/my-appointments/')
    
    if response.status_code == 200:
        print("   ✓ Page loaded successfully")
        
        # Check if price is in the response
        price_text = f"₹{service.base_price}"
        if price_text.encode() in response.content:
            print(f"   ✓ Price '{price_text}' found in page content")
        else:
            print(f"   ✗ Price '{price_text}' NOT found in page content")
            
        # Check for formatted price
        formatted_price = f"₹15000.00"
        if formatted_price.encode() in response.content:
            print(f"   ✓ Formatted price '{formatted_price}' found in page content")
        else:
            print(f"   ✗ Formatted price '{formatted_price}' NOT found in page content")
            
    else:
        print(f"   ✗ Page failed to load: {response.status_code}")
    
    # Test Appointment Detail page
    print(f"\n2. Testing Appointment Detail page...")
    response = client.get(f'/appointments/{appointment.id}/')
    
    if response.status_code == 200:
        print("   ✓ Page loaded successfully")
        
        # Check if price is in the response
        price_text = f"₹{service.base_price}"
        if price_text.encode() in response.content:
            print(f"   ✓ Price '{price_text}' found in page content")
        else:
            print(f"   ✗ Price '{price_text}' NOT found in page content")
            
        # Check for service name
        if service.name.encode() in response.content:
            print(f"   ✓ Service name '{service.name}' found in page content")
        else:
            print(f"   ✗ Service name '{service.name}' NOT found in page content")
            
        # Check for "Service Price:" label
        if b"Service Price:" in response.content:
            print("   ✓ 'Service Price:' label found in page content")
        else:
            print("   ✗ 'Service Price:' label NOT found in page content")
            
    else:
        print(f"   ✗ Page failed to load: {response.status_code}")
    
    # Test Service Detail page
    print(f"\n3. Testing Service Detail page...")
    response = client.get(f'/services/{service.id}/')
    
    if response.status_code == 200:
        print("   ✓ Page loaded successfully")
        
        # Check if price is in the response
        price_text = f"₹{service.base_price}"
        if price_text.encode() in response.content:
            print(f"   ✓ Price '{price_text}' found in service page")
        else:
            print(f"   ✗ Price '{price_text}' NOT found in service page")
            
    else:
        print(f"   ✗ Service page failed to load: {response.status_code}")
    
    print(f"\n" + "=" * 40)
    print("Price Display Test Summary")
    print("=" * 40)
    
    print(f"\nTest Data:")
    print(f"- Appointment ID: #{appointment.id}")
    print(f"- Service: {service.name}")
    print(f"- Service Price: ₹{service.base_price}")
    print(f"- Customer: {customer.username}")
    
    print(f"\nURLs to check manually:")
    print(f"- My Appointments: /appointments/my-appointments/")
    print(f"- Appointment Detail: /appointments/{appointment.id}/")
    print(f"- Service Detail: /services/{service.id}/")
    
    print(f"\n✅ Price display test completed!")

if __name__ == "__main__":
    test_price_display()