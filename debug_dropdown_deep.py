#!/usr/bin/env python
"""
Deep debug of dropdown issue - check form rendering and JavaScript
"""

import os
import sys
import django
from datetime import date, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carmodx.settings')
sys.path.append('/Users/vishavjeetsingh/untitled folder/untitled folder/detailcursor')

django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from appointments.forms import AppointmentBookingForm

User = get_user_model()

def debug_form_rendering():
    print("🔍 DEEP DEBUG: Form Rendering and JavaScript Issues")
    print("=" * 70)
    
    # Test form field generation
    user = User.objects.filter(role='customer').first()
    form = AppointmentBookingForm(user=user)
    
    print("\n📋 Form Field Details:")
    print(f"Date field ID: {form.fields['slot_date'].widget.attrs.get('id', 'NO ID')}")
    print(f"Time field ID: {form.fields['slot_time'].widget.attrs.get('id', 'slot-time-select')}")
    print(f"Date field label: {form['slot_date'].id_for_label}")
    print(f"Time field label: {form['slot_time'].id_for_label}")
    
    print(f"\n🔧 Time field choices:")
    for value, label in form.fields['slot_time'].choices:
        print(f"   '{value}' -> '{label}'")
    
    # Test client request to see actual HTML
    print(f"\n🌐 Testing actual booking page HTML...")
    client = Client()
    if user:
        client.force_login(user)
    
    response = client.get('/appointments/book/')
    print(f"Response status: {response.status_code}")
    
    if response.status_code == 200:
        html_content = response.content.decode()
        
        # Check for form elements
        if 'id="id_slot_date"' in html_content:
            print("✅ Date input found with ID: id_slot_date")
        else:
            print("❌ Date input ID not found")
            
        if 'id="slot-time-select"' in html_content:
            print("✅ Time select found with ID: slot-time-select")
        else:
            print("❌ Time select ID not found")
            
        # Check for JavaScript
        if 'loadAvailableSlots' in html_content:
            print("✅ JavaScript function loadAvailableSlots found")
        else:
            print("❌ JavaScript function not found")
            
        if 'addEventListener' in html_content:
            print("✅ Event listener code found")
        else:
            print("❌ Event listener code not found")
            
        # Check for API URL
        if '/appointments/api/available-slots/' in html_content:
            print("✅ API URL found in JavaScript")
        else:
            print("❌ API URL not found")
            
        # Extract the time select HTML
        import re
        select_pattern = r'<select[^>]*name="slot_time"[^>]*>(.*?)</select>'
        select_match = re.search(select_pattern, html_content, re.DOTALL)
        
        if select_match:
            select_html = select_match.group(0)
            print(f"\n📋 Time select HTML:")
            print(select_html[:200] + "..." if len(select_html) > 200 else select_html)
            
            # Count options
            option_count = select_html.count('<option')
            print(f"Options in HTML: {option_count}")
        else:
            print("❌ Could not find time select in HTML")
    else:
        print(f"❌ Failed to load booking page: {response.status_code}")
    
    # Test API directly
    print(f"\n🔌 Testing API directly...")
    tomorrow = date.today() + timedelta(days=1)
    api_response = client.get(f'/appointments/api/available-slots/?date={tomorrow}')
    
    if api_response.status_code == 200:
        data = api_response.json()
        print(f"✅ API working - {len(data.get('slots', []))} slots available")
        for slot in data.get('slots', []):
            print(f"   - {slot['time']} ({slot['display']})")
    else:
        print(f"❌ API error: {api_response.status_code}")
    
    print(f"\n" + "=" * 70)
    print(f"🎯 DIAGNOSIS CHECKLIST:")
    print(f"1. Form generates correct IDs")
    print(f"2. HTML contains form elements") 
    print(f"3. JavaScript is present")
    print(f"4. API is working")
    print(f"5. Event listeners are set up")
    print(f"\nIf all above are ✅, the issue might be:")
    print(f"- Browser JavaScript errors (check console)")
    print(f"- Caching issues (hard refresh)")
    print(f"- Network connectivity to API")

if __name__ == '__main__':
    debug_form_rendering()