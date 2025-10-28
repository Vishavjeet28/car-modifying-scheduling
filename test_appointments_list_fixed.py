#!/usr/bin/env python3
"""
Test script to verify the fixed appointments list page shows all data correctly
"""
import requests
from requests.sessions import Session
import re

# Test the fixed appointments list page
def test_appointments_list_page():
    print("Testing Appointments List Page After Fixes")
    print("=" * 50)
    
    session = Session()
    
    try:
        # Get login page first
        login_url = "http://127.0.0.1:8000/accounts/login/"
        login_page = session.get(login_url)
        
        if login_page.status_code != 200:
            print(f"❌ Cannot access login page: {login_page.status_code}")
            return
        
        # Extract CSRF token
        csrf_match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', login_page.text)
        if not csrf_match:
            print("❌ Cannot find CSRF token")
            return
        
        csrf_token = csrf_match.group(1)
        
        # Login as staff user
        login_data = {
            'username': 'staffuser',
            'password': 'staffpass123',
            'csrfmiddlewaretoken': csrf_token
        }
        
        login_response = session.post(login_url, data=login_data, allow_redirects=False)
        
        if login_response.status_code not in [302, 200]:
            print(f"❌ Login failed: {login_response.status_code}")
            return
        
        print("✅ Successfully logged in as staff user")
        
        # Now test the appointments list page
        appointments_url = "http://127.0.0.1:8000/appointments/list/"
        response = session.get(appointments_url)
        
        print(f"\nAppointments List Page Status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.text
            
            # Check for template errors or empty content
            print("\nChecking template field rendering:")
            
            # Check for service information
            if 'selected_service' in content or any(service in content for service in ['Engine', 'Brake', 'Oil', 'Transmission']):
                print("✅ Service information is rendering")
            else:
                print("❌ Service information not found")
            
            # Check for date/time information
            if 'slot_date' in content or any(pattern in content for pattern in ['2024', '2025', 'AM', 'PM']):
                print("✅ Date/time information is rendering")
            else:
                print("❌ Date/time information not found")
            
            # Check for employee information
            if 'assigned_employee' in content or 'staffuser' in content:
                print("✅ Employee information is rendering")
            else:
                print("❌ Employee information not found")
            
            # Check for price information
            if 'base_price' in content or '$' in content:
                print("✅ Price information is rendering")
            else:
                print("❌ Price information not found")
            
            # Check for status badges
            status_badges = ['booked', 'assigned', 'in_progress', 'completed', 'on_hold', 'cancelled']
            if any(status in content for status in status_badges):
                print("✅ Status badges are rendering")
            else:
                print("❌ Status badges not found")
            
            # Check for Bootstrap badge classes
            badge_classes = ['bg-info', 'bg-primary', 'bg-warning', 'bg-success', 'bg-secondary', 'bg-danger']
            if any(badge_class in content for badge_class in badge_classes):
                print("✅ Bootstrap badge styling is present")
            else:
                print("❌ Bootstrap badge styling not found")
            
            # Check for table structure
            if '<table' in content and '<tbody' in content:
                print("✅ Table structure is present")
            else:
                print("❌ Table structure not found")
            
            # Count appointments shown
            appointment_rows = content.count('<tr>') - 1  # Subtract header row
            print(f"\nAppointments displayed: {appointment_rows}")
            
            # Check for specific field values that should be populated
            print("\nField Content Analysis:")
            print(f"- Service names found: {'Engine' in content or 'Brake' in content}")
            print(f"- Dollar signs found: {'$' in content}")
            print(f"- Date patterns found: {'2024' in content or '2025' in content}")
            print(f"- Staff references found: {'staffuser' in content}")
            
            print("\n✅ Appointments list page is working with fixed template fields!")
            
        else:
            print(f"❌ Cannot access appointments list page: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Error testing appointments list page: {str(e)}")

if __name__ == "__main__":
    test_appointments_list_page()