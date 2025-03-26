#!/usr/bin/env python
import os
import sys
import django
from django.core.management import call_command

# Set up Django environment
sys.path.append('/home/ubuntu/agritech_prototype')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agritech.settings')
django.setup()

def run_tests():
    """Run automated tests for the AgriTech prototype."""
    print("=== Running AgriTech Prototype Tests ===")
    
    # Test database connections
    print("\n[1/5] Testing database connection...")
    try:
        from django.db import connections
        connections['default'].ensure_connection()
        print("✓ Database connection successful")
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
    
    # Test model integrity
    print("\n[2/5] Testing model integrity...")
    try:
        from marketplace.models import Farmer, Buyer, Produce, Order, Rating
        from sms_service.models import SMSMessage, SMSTemplate, WeatherAlert, PriceUpdate
        
        print(f"✓ Marketplace models loaded successfully")
        print(f"✓ SMS Service models loaded successfully")
    except Exception as e:
        print(f"✗ Model integrity check failed: {e}")
    
    # Test URL configurations
    print("\n[3/5] Testing URL configurations...")
    try:
        from django.urls import reverse, NoReverseMatch
        
        # Test marketplace URLs
        marketplace_urls = ['marketplace_home', 'produce_list', 'create_produce']
        for url_name in marketplace_urls:
            reverse(url_name)
        print(f"✓ Marketplace URLs configured correctly")
        
        # Test SMS service URLs
        sms_urls = ['sms_dashboard', 'send_sms', 'sms_history']
        for url_name in sms_urls:
            reverse(url_name)
        print(f"✓ SMS Service URLs configured correctly")
        
        # Test admin URLs
        admin_urls = ['admin_dashboard', 'admin_users', 'admin_produce', 'admin_orders']
        for url_name in admin_urls:
            reverse(url_name)
        print(f"✓ Admin URLs configured correctly")
    except NoReverseMatch as e:
        print(f"✗ URL configuration check failed: {e}")
    
    # Test template rendering
    print("\n[4/5] Testing template rendering...")
    try:
        from django.template.loader import render_to_string
        
        # Test marketplace templates
        marketplace_templates = [
            'marketplace/home.html',
            'marketplace/produce_list.html',
            'marketplace/produce_detail.html',
            'marketplace/create_produce.html',
            'marketplace/order_list.html',
            'marketplace/order_detail.html'
        ]
        
        for template in marketplace_templates:
            render_to_string(template, {})
        print(f"✓ Marketplace templates render correctly")
        
        # Test SMS service templates
        sms_templates = [
            'sms_service/dashboard.html',
            'sms_service/send_sms.html',
            'sms_service/sms_history.html',
            'sms_service/weather_alert_list.html',
            'sms_service/price_update_list.html',
            'sms_service/template_list.html'
        ]
        
        for template in sms_templates:
            render_to_string(template, {})
        print(f"✓ SMS Service templates render correctly")
        
        # Test admin templates
        admin_templates = [
            'admin/dashboard.html',
            'admin/users.html',
            'admin/produce.html',
            'admin/orders.html'
        ]
        
        for template in admin_templates:
            render_to_string(template, {})
        print(f"✓ Admin templates render correctly")
    except Exception as e:
        print(f"✗ Template rendering check failed: {e}")
    
    # Test static files
    print("\n[5/5] Testing static files...")
    try:
        static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
        if os.path.exists(static_dir):
            css_file = os.path.join(static_dir, 'css', 'style.css')
            if os.path.exists(css_file):
                print(f"✓ Static CSS files exist")
            else:
                print(f"✗ CSS file not found: {css_file}")
        else:
            print(f"✗ Static directory not found: {static_dir}")
    except Exception as e:
        print(f"✗ Static files check failed: {e}")
    
    print("\n=== Test Summary ===")
    print("The AgriTech prototype has been tested for basic functionality.")
    print("Note: This is a simplified test. For production, more comprehensive tests would be needed.")

if __name__ == "__main__":
    run_tests()
