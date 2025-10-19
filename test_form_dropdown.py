#!/usr/bin/env python
"""
Test that the form dropdown starts empty and only shows available slots
"""

import os
import sys
import django
from datetime import date, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carmodx.settings')
sys.path.append('/Users/vishavjeetsingh/untitled folder/untitled folder/detailcursor')

django.setup()

from appointments.forms import AppointmentBookingForm
from django.contrib.auth import get_user_model

User = get_user_model()

def test_form_dropdown():
    print("🔍 Testing Form Dropdown Initial State")
    print("=" * 60)
    
    # Create form
    user = User.objects.filter(role='customer').first()
    form = AppointmentBookingForm(user=user)
    
    # Check slot_time field choices
    print("\n📋 Initial slot_time dropdown options:")
    for value, label in form.fields['slot_time'].choices:
        print(f"   Value: '{value}' | Label: '{label}'")
    
    print(f"\n📊 Total options in dropdown: {len(form.fields['slot_time'].choices)}")
    
    if len(form.fields['slot_time'].choices) == 1:
        print("✅ CORRECT: Only 1 option (the placeholder)")
        print("✅ No time slots pre-populated")
        print("✅ JavaScript will populate with available slots only")
    else:
        print(f"❌ PROBLEM: {len(form.fields['slot_time'].choices)} options found")
        print("❌ Time slots are pre-populated in the form")
        print("❌ This causes all slots to show before JavaScript runs")
    
    print("\n" + "=" * 60)
    print("🎯 Expected behavior:")
    print("1. Page loads with empty dropdown (just placeholder)")
    print("2. User selects a date")
    print("3. JavaScript fetches available slots from API")
    print("4. Dropdown populated with ONLY available (unbooked) slots")

if __name__ == '__main__':
    test_form_dropdown()