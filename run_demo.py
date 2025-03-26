#!/usr/bin/env python
import os
import sys
import django
import subprocess
import time

# Set up Django environment
sys.path.append('/home/ubuntu/agritech_prototype')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agritech.settings')
django.setup()

def run_demo_server():
    """Run the AgriTech prototype demo server."""
    print("=== Starting AgriTech Prototype Demo Server ===")
    
    # Check if test data exists
    from django.contrib.auth.models import User
    from marketplace.models import Produce
    
    if User.objects.count() <= 1 or Produce.objects.count() == 0:
        print("\n[1/4] Test data not found. Creating sample data...")
        try:
            subprocess.run(['python', 'tests/create_test_data.py'], check=True)
            print("✓ Sample data created successfully")
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to create sample data: {e}")
            return
    else:
        print("\n[1/4] Sample data already exists. Skipping data creation.")
    
    # Collect static files
    print("\n[2/4] Collecting static files...")
    try:
        from django.core.management import call_command
        call_command('collectstatic', '--noinput')
        print("✓ Static files collected successfully")
    except Exception as e:
        print(f"✗ Failed to collect static files: {e}")
    
    # Run basic tests
    print("\n[3/4] Running basic tests...")
    try:
        subprocess.run(['python', 'tests/test_prototype.py'], check=True)
        print("✓ Basic tests completed successfully")
    except subprocess.CalledProcessError as e:
        print(f"✗ Basic tests failed: {e}")
    
    # Start the development server
    print("\n[4/4] Starting development server...")
    print("The AgriTech prototype is now running at: http://localhost:8000/")
    print("\nLogin credentials:")
    print("Admin: username=admin, password=admin123")
    print("Farmer: username=mohamed, password=password123")
    print("Buyer: username=salah, password=password123")
    print("\nPress Ctrl+C to stop the server.")
    
    try:
        # Start the server on 0.0.0.0 to make it accessible externally
        subprocess.run(['python', 'manage.py', 'runserver', '0.0.0.0:8000'], check=True)
    except KeyboardInterrupt:
        print("\nServer stopped.")
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to start development server: {e}")

if __name__ == "__main__":
    run_demo_server()
