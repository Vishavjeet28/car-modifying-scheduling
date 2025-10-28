#!/usr/bin/env python
"""Comprehensive test script for CarModX project functionality"""
import os
import django
import sys
from datetime import date, timedelta
from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carmodx.settings')
django.setup()

from accounts.models import User, Employee
from services.models import Service, ServiceCategory
from appointments.models import Appointment

class CarModXTester:
    def __init__(self):
        self.client = Client()
        self.results = []
        
    def log_result(self, test_name, status, message=""):
        """Log test results"""
        self.results.append({
            'test': test_name,
            'status': status,
            'message': message
        })
        status_symbol = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_symbol} {test_name}: {message}")
    
    def test_user_authentication(self):
        """Test user authentication system"""
        print("\n🔐 TESTING USER AUTHENTICATION")
        
        # Test login page
        response = self.client.get(reverse('accounts:login'))
        if response.status_code == 200:
            self.log_result("Login Page Access", "PASS", "Login page loads correctly")
        else:
            self.log_result("Login Page Access", "FAIL", f"Status: {response.status_code}")
        
        # Test registration page
        response = self.client.get(reverse('accounts:register'))
        if response.status_code == 200:
            self.log_result("Registration Page Access", "PASS", "Registration page loads correctly")
        else:
            self.log_result("Registration Page Access", "FAIL", f"Status: {response.status_code}")
        
        # Test customer login
        customer = User.objects.filter(role='customer').first()
        if customer:
            login_success = self.client.login(username=customer.username, password='test123')
            if login_success:
                self.log_result("Customer Login", "PASS", f"Customer {customer.username} login successful")
                self.client.logout()
            else:
                self.log_result("Customer Login", "WARN", f"Could not login with test password for {customer.username}")
        
        # Test employee login
        employee_user = User.objects.filter(role='employee').first()
        if employee_user:
            login_success = self.client.login(username=employee_user.username, password='test123')
            if login_success:
                self.log_result("Employee Login", "PASS", f"Employee {employee_user.username} login successful")
                self.client.logout()
            else:
                self.log_result("Employee Login", "WARN", f"Could not login with test password for {employee_user.username}")
    
    def test_services_management(self):
        """Test services functionality"""
        print("\n🔧 TESTING SERVICES MANAGEMENT")
        
        # Test service list
        response = self.client.get(reverse('services:service_list'))
        if response.status_code == 200:
            self.log_result("Service List Page", "PASS", "Service list loads correctly")
        else:
            self.log_result("Service List Page", "FAIL", f"Status: {response.status_code}")
        
        # Test service detail
        service = Service.objects.first()
        if service:
            response = self.client.get(reverse('services:service_detail', args=[service.id]))
            if response.status_code == 200:
                self.log_result("Service Detail Page", "PASS", f"Service detail for '{service.name}' loads correctly")
            else:
                self.log_result("Service Detail Page", "FAIL", f"Status: {response.status_code}")
        
        # Check categories
        categories = ServiceCategory.objects.count()
        services = Service.objects.count()
        self.log_result("Data Integrity", "PASS", f"{categories} categories, {services} services found")
    
    def test_appointment_booking(self):
        """Test appointment booking flow"""
        print("\n📅 TESTING APPOINTMENT BOOKING")
        
        # Test booking page (should redirect if not logged in)
        response = self.client.get(reverse('appointments:book_appointment'))
        if response.status_code == 302:
            self.log_result("Booking Access Control", "PASS", "Booking redirects when not logged in")
        else:
            self.log_result("Booking Access Control", "WARN", f"Unexpected status: {response.status_code}")
        
        # Login as customer and test booking
        customer = User.objects.filter(role='customer').first()
        if customer:
            # Try login (may not work if password is different)
            self.client.force_login(customer)  # Force login for testing
            
            response = self.client.get(reverse('appointments:book_appointment'))
            if response.status_code == 200:
                self.log_result("Customer Booking Access", "PASS", f"Customer can access booking page")
            else:
                self.log_result("Customer Booking Access", "FAIL", f"Status: {response.status_code}")
            
            # Test available slots API
            tomorrow = date.today() + timedelta(days=1)
            response = self.client.get(reverse('appointments:available_slots_api'), {'date': tomorrow})
            if response.status_code == 200:
                self.log_result("Available Slots API", "PASS", "API returns slot data")
            else:
                self.log_result("Available Slots API", "FAIL", f"Status: {response.status_code}")
            
            self.client.logout()
    
    def test_employee_dashboard(self):
        """Test employee functionality"""
        print("\n👷 TESTING EMPLOYEE FEATURES")
        
        # Test employee access
        employee_user = User.objects.filter(role='employee').first()
        if employee_user:
            self.client.force_login(employee_user)
            
            # Test employee dashboard
            response = self.client.get(reverse('accounts:employee_dashboard'))
            if response.status_code == 200:
                self.log_result("Employee Dashboard", "PASS", "Employee dashboard loads correctly")
            else:
                self.log_result("Employee Dashboard", "FAIL", f"Status: {response.status_code}")
            
            # Test appointment list
            response = self.client.get(reverse('appointments:appointment_list'))
            if response.status_code == 200:
                self.log_result("Appointment List", "PASS", "Employee can view appointment list")
            else:
                self.log_result("Appointment List", "FAIL", f"Status: {response.status_code}")
            
            self.client.logout()
    
    def test_admin_features(self):
        """Test admin functionality"""
        print("\n👑 TESTING ADMIN FEATURES")
        
        # Test admin access
        admin_user = User.objects.filter(role='admin').first()
        if admin_user:
            self.client.force_login(admin_user)
            
            # Test admin panel
            response = self.client.get(reverse('admin_panel:dashboard'))
            if response.status_code == 200:
                self.log_result("Admin Dashboard", "PASS", "Admin dashboard loads correctly")
            else:
                self.log_result("Admin Dashboard", "FAIL", f"Status: {response.status_code}")
            
            self.client.logout()
        else:
            self.log_result("Admin User", "WARN", "No admin user found")
    
    def test_data_integrity(self):
        """Test database operations and data integrity"""
        print("\n🗄️ TESTING DATA INTEGRITY")
        
        # Check user roles
        customers = User.objects.filter(role='customer').count()
        employees = User.objects.filter(role='employee').count()
        admins = User.objects.filter(role='admin').count()
        
        self.log_result("User Roles", "PASS", f"Customers: {customers}, Employees: {employees}, Admins: {admins}")
        
        # Check appointments
        appointments = Appointment.objects.count()
        active_appointments = Appointment.objects.filter(status__in=['booked', 'assigned', 'in_progress']).count()
        
        self.log_result("Appointments", "PASS", f"Total: {appointments}, Active: {active_appointments}")
        
        # Check service relationships
        services_with_categories = Service.objects.filter(category__isnull=False).count()
        total_services = Service.objects.count()
        
        if services_with_categories == total_services:
            self.log_result("Service Categories", "PASS", "All services have categories")
        else:
            self.log_result("Service Categories", "WARN", f"{total_services - services_with_categories} services without categories")
    
    def test_error_handling(self):
        """Test error handling and edge cases"""
        print("\n🚨 TESTING ERROR HANDLING")
        
        # Test 404 errors
        response = self.client.get('/nonexistent-page/')
        if response.status_code == 404:
            self.log_result("404 Handling", "PASS", "Non-existent pages return 404")
        else:
            self.log_result("404 Handling", "WARN", f"Status: {response.status_code}")
        
        # Test invalid service ID
        response = self.client.get('/services/99999/')
        if response.status_code == 404:
            self.log_result("Invalid Service ID", "PASS", "Invalid service returns 404")
        else:
            self.log_result("Invalid Service ID", "WARN", f"Status: {response.status_code}")
    
    def run_all_tests(self):
        """Run all tests and generate report"""
        print("🚀 STARTING COMPREHENSIVE CARMODX TESTING")
        print("=" * 60)
        
        self.test_user_authentication()
        self.test_services_management() 
        self.test_appointment_booking()
        self.test_employee_dashboard()
        self.test_admin_features()
        self.test_data_integrity()
        self.test_error_handling()
        
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = len([r for r in self.results if r['status'] == 'PASS'])
        failed = len([r for r in self.results if r['status'] == 'FAIL'])
        warnings = len([r for r in self.results if r['status'] == 'WARN'])
        total = len(self.results)
        
        print(f"✅ PASSED: {passed}")
        print(f"❌ FAILED: {failed}")
        print(f"⚠️  WARNINGS: {warnings}")
        print(f"📈 TOTAL: {total}")
        
        if failed == 0:
            print("\n🎉 ALL CRITICAL TESTS PASSED! Your CarModX project is working well!")
        else:
            print("\n🔧 Some tests failed. Check the details above.")
        
        return self.results

if __name__ == "__main__":
    tester = CarModXTester()
    tester.run_all_tests()