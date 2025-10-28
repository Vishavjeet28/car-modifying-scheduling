#!/usr/bin/env python
"""
Script to populate the database with sample data for CarModX
"""
import os
import sys
import django
from datetime import date, time, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carmodx.settings')
django.setup()

from accounts.models import User, Employee
from services.models import ServiceCategory, Service, ServicePrice
from appointments.models import TimeSlot, Appointment
from django.utils import timezone

def create_sample_data():
    print("Creating sample data for CarModX...")
    
    # Create service categories
    categories_data = [
        {'name': 'Performance', 'description': 'Engine and performance modifications', 'icon': 'fas fa-tachometer-alt'},
        {'name': 'Exterior', 'description': 'Body kits, paint, and exterior styling', 'icon': 'fas fa-car'},
        {'name': 'Interior', 'description': 'Seats, dashboard, and interior upgrades', 'icon': 'fas fa-chair'},
        {'name': 'Audio & Electronics', 'description': 'Sound systems and electronic upgrades', 'icon': 'fas fa-volume-up'},
        {'name': 'Wheels & Tires', 'description': 'Custom wheels and tire upgrades', 'icon': 'fas fa-circle'},
    ]
    
    categories = {}
    for cat_data in categories_data:
        category, created = ServiceCategory.objects.get_or_create(
            name=cat_data['name'],
            defaults=cat_data
        )
        categories[cat_data['name']] = category
        print(f"Created category: {category.name}")
    
    # Create services
    services_data = [
        {
            'name': 'Engine Tuning',
            'description': 'Professional engine tuning for improved performance and fuel efficiency.',
            'category': 'Performance',
            'base_price': 299.99,
            'estimated_duration': timedelta(hours=3)
        },
        {
            'name': 'Turbo Installation',
            'description': 'Complete turbocharger installation with all necessary components.',
            'category': 'Performance',
            'base_price': 2499.99,
            'estimated_duration': timedelta(hours=8)
        },
        {
            'name': 'Body Kit Installation',
            'description': 'Custom body kit installation and paint matching.',
            'category': 'Exterior',
            'base_price': 1299.99,
            'estimated_duration': timedelta(hours=6)
        },
        {
            'name': 'Custom Paint Job',
            'description': 'Professional custom paint job with premium materials.',
            'category': 'Exterior',
            'base_price': 1999.99,
            'estimated_duration': timedelta(hours=12)
        },
        {
            'name': 'Leather Seat Upgrade',
            'description': 'Premium leather seat installation and customization.',
            'category': 'Interior',
            'base_price': 899.99,
            'estimated_duration': timedelta(hours=4)
        },
        {
            'name': 'Custom Dashboard',
            'description': 'Custom dashboard design and installation.',
            'category': 'Interior',
            'base_price': 1599.99,
            'estimated_duration': timedelta(hours=8)
        },
        {
            'name': 'Premium Sound System',
            'description': 'High-end audio system installation with subwoofers and amplifiers.',
            'category': 'Audio & Electronics',
            'base_price': 799.99,
            'estimated_duration': timedelta(hours=5)
        },
        {
            'name': 'Custom Wheels',
            'description': 'Custom alloy wheels installation with tire mounting.',
            'category': 'Wheels & Tires',
            'base_price': 599.99,
            'estimated_duration': timedelta(hours=2)
        },
    ]
    
    services = {}
    for service_data in services_data:
        service, created = Service.objects.get_or_create(
            name=service_data['name'],
            defaults={
                'description': service_data['description'],
                'category': categories[service_data['category']],
                'base_price': service_data['base_price'],
                'estimated_duration': service_data['estimated_duration']
            }
        )
        services[service_data['name']] = service
        print(f"Created service: {service.name}")
    
    # Create employees
    employees_data = [
        {
            'username': 'john_mechanic',
            'email': 'john@carmodx.com',
            'first_name': 'John',
            'last_name': 'Smith',
            'employee_id': 'EMP001',
            'specialization': 'Engine Performance',
            'hire_date': date(2020, 1, 15)
        },
        {
            'username': 'sarah_painter',
            'email': 'sarah@carmodx.com',
            'first_name': 'Sarah',
            'last_name': 'Johnson',
            'employee_id': 'EMP002',
            'specialization': 'Body Work & Paint',
            'hire_date': date(2019, 6, 10)
        },
        {
            'username': 'mike_audio',
            'email': 'mike@carmodx.com',
            'first_name': 'Mike',
            'last_name': 'Davis',
            'employee_id': 'EMP003',
            'specialization': 'Audio & Electronics',
            'hire_date': date(2021, 3, 20)
        },
    ]
    
    employees = {}
    for emp_data in employees_data:
        user, created = User.objects.get_or_create(
            username=emp_data['username'],
            defaults={
                'email': emp_data['email'],
                'first_name': emp_data['first_name'],
                'last_name': emp_data['last_name'],
                'role': 'employee'
            }
        )
        if created:
            user.set_password('employee123')
            user.save()
        
        employee, created = Employee.objects.get_or_create(
            user=user,
            defaults={
                'employee_id': emp_data['employee_id'],
                'specialization': emp_data['specialization'],
                'hire_date': emp_data['hire_date']
            }
        )
        employees[emp_data['username']] = employee
        print(f"Created employee: {employee.user.get_full_name()}")
    
    # Create time slots for the next 30 days
    print("Creating time slots...")
    start_date = date.today()
    for i in range(30):
        current_date = start_date + timedelta(days=i)
        
        # Create time slots for each day (9 AM to 5 PM, every 2 hours)
        for hour in range(9, 17, 2):
            start_time = time(hour, 0)
            end_time = time(hour + 2, 0)
            
            TimeSlot.objects.get_or_create(
                date=current_date,
                start_time=start_time,
                defaults={
                    'end_time': end_time,
                    'is_available': True,
                    'max_appointments': 3
                }
            )
    
    print("Sample data created successfully!")
    print(f"Created {ServiceCategory.objects.count()} categories")
    print(f"Created {Service.objects.count()} services")
    print(f"Created {Employee.objects.count()} employees")
    print(f"Created {TimeSlot.objects.count()} time slots")

if __name__ == '__main__':
    create_sample_data()
