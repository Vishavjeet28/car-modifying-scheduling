#!/usr/bin/env python
"""
Test admin panel services functionality
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carmodx.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model

User = get_user_model()

def test_admin_panel_services():
    print("🔍 TESTING ADMIN PANEL SERVICES PAGE")
    print("=" * 50)
    
    client = Client()
    
    # Get admin user
    admin = User.objects.filter(is_superuser=True).first()
    if not admin:
        print("❌ No admin users found")
        return
    
    print(f"✅ Testing with admin: {admin.username}")
    
    # Test without login (should redirect)
    response = client.get('/admin-panel/services/')
    print(f"📝 Without login: {response.status_code} (should be 302 redirect)")
    
    # Login as admin
    client.force_login(admin)
    
    # Test admin panel services page
    response = client.get('/admin-panel/services/')
    print(f"📝 Admin services page: {response.status_code} (should be 200)")
    
    if response.status_code == 200:
        content = response.content.decode()
        
        # Check key elements
        checks = [
            ('Service Management Title', 'Service Management' in content),
            ('Services Table', 'Services List' in content),
            ('View Button Function', 'viewServiceDetails' in content),
            ('Delete Button Function', 'confirmDelete' in content),
            ('Correct URLs in JS', '/admin-panel/services/' in content),
            ('Modal Elements', 'serviceDetailsModal' in content),
            ('Delete Modal', 'deleteConfirmModal' in content),
        ]
        
        print("\n🔍 Content Analysis:")
        for check_name, result in checks:
            status = "✅" if result else "❌"
            print(f"{status} {check_name}: {result}")
        
        # Test AJAX detail endpoint
        from services.models import Service
        service = Service.objects.first()
        if service:
            ajax_response = client.get(f'/admin-panel/services/{service.id}/detail/')
            print(f"📝 AJAX detail endpoint: {ajax_response.status_code}")
            
            if ajax_response.status_code == 200:
                print("✅ Service detail AJAX endpoint working")
            else:
                print(f"❌ Service detail AJAX endpoint failed: {ajax_response.status_code}")
        
        # Test delete URL structure
        if service:
            delete_url = f'/admin-panel/services/{service.id}/delete/'
            print(f"📝 Delete URL pattern: {delete_url}")
            delete_response = client.get(delete_url)
            print(f"📝 Delete page access: {delete_response.status_code}")
    
    else:
        print(f"❌ Admin services page failed: {response.status_code}")
        if hasattr(response, 'content'):
            print("Error content:", response.content.decode()[:200])

if __name__ == "__main__":
    test_admin_panel_services()