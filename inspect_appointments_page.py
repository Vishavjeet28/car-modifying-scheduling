#!/usr/bin/env python3
"""
Direct content inspection of the appointments list page
"""
import requests
from requests.sessions import Session
import re

def inspect_appointments_page():
    print("Inspecting Appointments List Page Content")
    print("=" * 50)
    
    session = Session()
    
    try:
        # Login first
        login_url = "http://127.0.0.1:8000/accounts/login/"
        login_page = session.get(login_url)
        csrf_match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', login_page.text)
        csrf_token = csrf_match.group(1)
        
        login_data = {
            'username': 'staffuser',
            'password': 'staffpass123',
            'csrfmiddlewaretoken': csrf_token
        }
        
        session.post(login_url, data=login_data, allow_redirects=False)
        
        # Get appointments list page
        appointments_url = "http://127.0.0.1:8000/appointments/list/"
        response = session.get(appointments_url)
        
        if response.status_code == 200:
            content = response.text
            
            # Extract the main content area
            if '<tbody>' in content:
                tbody_start = content.find('<tbody>')
                tbody_end = content.find('</tbody>', tbody_start)
                if tbody_end != -1:
                    tbody_content = content[tbody_start:tbody_end + 8]
                    print("Table body content:")
                    print(tbody_content[:500] + "..." if len(tbody_content) > 500 else tbody_content)
            else:
                print("No <tbody> found. Looking for appointment data:")
                # Look for any appointment-related content
                if 'appointment' in content.lower():
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if 'appointment' in line.lower():
                            print(f"Line {i}: {line.strip()}")
                            # Print surrounding lines for context
                            for j in range(max(0, i-2), min(len(lines), i+3)):
                                if j != i:
                                    print(f"  {j}: {lines[j].strip()}")
                            break
            
            # Check if there are any appointments in the database
            print("\nChecking for appointment count in page...")
            if 'No appointments found' in content or 'no appointments' in content.lower():
                print("❌ No appointments message found in page")
            else:
                print("✅ Page doesn't show 'no appointments' message")
                
        else:
            print(f"Failed to get page: {response.status_code}")
    
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    inspect_appointments_page()