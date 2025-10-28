#!/usr/bin/env python
"""
COMPREHENSIVE TEMPLATE VALIDATION SCRIPT
Finds template-model field mismatches across ALL templates
"""
import os
import django
import re
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carmodx.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.template.loader import get_template
from django.template import TemplateDoesNotExist

User = get_user_model()

class TemplateValidator:
    def __init__(self):
        self.client = Client()
        self.errors_found = []
        self.templates_checked = 0
        
    def log_error(self, template_path, error_type, details):
        """Log template errors"""
        self.errors_found.append({
            'template': template_path,
            'error_type': error_type,
            'details': details
        })
        print(f"❌ {template_path}: {error_type} - {details}")
    
    def extract_template_variables(self, template_content):
        """Extract Django template variables from content"""
        # Find all {{ variable }} patterns
        variable_pattern = r'{{\s*([^}]+)\s*}}'
        variables = re.findall(variable_pattern, template_content)
        
        # Clean up variables (remove filters, etc.)
        clean_variables = []
        for var in variables:
            # Remove filters (e.g., |date:"M d, Y")
            clean_var = var.split('|')[0].strip()
            # Remove method calls with parameters
            clean_var = re.sub(r'\([^)]*\)', '', clean_var)
            clean_variables.append(clean_var)
        
        return clean_variables
    
    def check_all_account_templates(self):
        """Check all templates in accounts app"""
        print("🔍 CHECKING ALL ACCOUNTS TEMPLATES")
        print("=" * 50)
        
        accounts_template_dir = Path("templates/accounts")
        if not accounts_template_dir.exists():
            print("❌ Accounts template directory not found")
            return
        
        # Get all customer, employee, admin users for testing
        customer = User.objects.filter(role='customer').first()
        employee = User.objects.filter(role='employee').first()
        admin = User.objects.filter(role='admin').first()
        
        # Define all account URLs to test
        account_urls = [
            ('accounts:dashboard', [], customer),
            ('accounts:employee_dashboard', [], employee),
            ('accounts:admin_dashboard', [], admin),
            ('accounts:profile', [], customer),
            ('accounts:appointment_history', [], customer),
        ]
        
        for url_name, args, user in account_urls:
            if not user:
                print(f"⚠️ Skipping {url_name} - no user of required type")
                continue
                
            try:
                print(f"\n🔍 Testing {url_name}...")
                self.client.force_login(user)
                
                url = reverse(url_name, args=args)
                response = self.client.get(url)
                
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    # Check for template variable errors in content
                    content = response.content.decode()
                    self.check_template_content_for_errors(url_name, content)
                elif response.status_code == 302:
                    print(f"   Redirected (normal for some user types)")
                else:
                    self.log_error(url_name, "HTTP_ERROR", f"Status {response.status_code}")
                    
            except Exception as e:
                self.log_error(url_name, "EXCEPTION", str(e))
    
    def check_template_content_for_errors(self, template_name, content):
        """Check rendered template content for common error patterns"""
        error_patterns = [
            (r'VariableDoesNotExist', 'VARIABLE_NOT_EXIST'),
            (r'AttributeError', 'ATTRIBUTE_ERROR'),
            (r'TemplateSyntaxError', 'SYNTAX_ERROR'),
            (r'NoReverseMatch', 'URL_REVERSE_ERROR'),
            (r'RelatedObjectDoesNotExist', 'RELATED_OBJECT_ERROR'),
            (r'DoesNotExist', 'OBJECT_NOT_EXIST'),
        ]
        
        for pattern, error_type in error_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                self.log_error(template_name, error_type, f"Found {pattern} in rendered content")
    
    def check_all_templates_systematically(self):
        """Check all template files for potential field mismatches"""
        print("\n🔍 SYSTEMATIC TEMPLATE FILE ANALYSIS")
        print("=" * 50)
        
        template_dirs = [
            "templates/accounts",
            "templates/appointments", 
            "templates/services",
            "templates/admin_panel"
        ]
        
        for template_dir in template_dirs:
            template_path = Path(template_dir)
            if not template_path.exists():
                continue
                
            print(f"\n📁 Checking {template_dir}/")
            
            for template_file in template_path.glob("*.html"):
                self.templates_checked += 1
                print(f"   📄 {template_file.name}")
                
                try:
                    with open(template_file, 'r') as f:
                        content = f.read()
                    
                    # Extract variables
                    variables = self.extract_template_variables(content)
                    
                    # Check for suspicious patterns
                    suspicious_patterns = [
                        'appointment.service.',  # Should be appointment.selected_service
                        'appointment.time_slot.',  # Should be appointment.slot_date/slot_time
                        'appointment.estimated_price',  # Should be selected_service.base_price
                        'appointment.employee.',  # Should be appointment.assigned_employee
                        '.price',  # Check if it should be base_price
                        '.confirmed',  # Old status
                        '.pending',  # Old status  
                    ]
                    
                    for pattern in suspicious_patterns:
                        if pattern in content:
                            self.log_error(str(template_file), "SUSPICIOUS_FIELD", 
                                         f"Found potentially outdated field: {pattern}")
                
                except Exception as e:
                    self.log_error(str(template_file), "FILE_ERROR", str(e))
    
    def run_complete_validation(self):
        """Run all validation checks"""
        print("🚀 COMPREHENSIVE TEMPLATE VALIDATION")
        print("=" * 60)
        
        # Check all account pages with actual users
        self.check_all_account_templates()
        
        # Check template files systematically
        self.check_all_templates_systematically()
        
        # Summary
        print(f"\n📊 VALIDATION SUMMARY")
        print("=" * 40)
        print(f"Templates checked: {self.templates_checked}")
        print(f"Errors found: {len(self.errors_found)}")
        
        if self.errors_found:
            print(f"\n🚨 ERRORS REQUIRING ATTENTION:")
            for error in self.errors_found:
                print(f"❌ {error['template']}: {error['error_type']}")
                print(f"   {error['details']}")
        else:
            print(f"\n✅ NO TEMPLATE ERRORS FOUND!")
        
        return len(self.errors_found) == 0

if __name__ == "__main__":
    validator = TemplateValidator()
    success = validator.run_complete_validation()
    
    if not success:
        print(f"\n⚠️ RECOMMENDATION: Review and fix template errors above")
    else:
        print(f"\n🎉 ALL TEMPLATES VALIDATED SUCCESSFULLY!")