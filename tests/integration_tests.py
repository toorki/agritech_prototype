#!/usr/bin/env python
import os
import sys
import django
from django.core.management import call_command

# Set up Django environment
sys.path.append('/home/ubuntu/agritech_prototype')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agritech.settings')
django.setup()

def run_integration_tests():
    """Run integration tests for the AgriTech prototype."""
    print("=== Running AgriTech Prototype Integration Tests ===")
    
    # Import models
    from django.contrib.auth.models import User
    from marketplace.models import Farmer, Buyer, Category, Produce, Order, Rating
    from sms_service.models import SMSMessage, SMSTemplate, WeatherAlert, PriceUpdate
    
    # Test 1: Order Creation Flow
    print("\n[1/5] Testing Order Creation Flow...")
    try:
        # Get a buyer, farmer and produce
        buyer = Buyer.objects.first()
        produce = Produce.objects.filter(is_available=True).first()
        
        if not buyer or not produce:
            print("✗ Test data not available. Please run create_test_data.py first.")
        else:
            # Create a new order
            initial_quantity = produce.quantity
            order_quantity = min(2, initial_quantity)
            
            order = Order.objects.create(
                buyer=buyer,
                produce=produce,
                quantity=order_quantity,
                unit_price=produce.price_per_unit,
                total_price=order_quantity * produce.price_per_unit,
                status='pending',
                shipping_address=buyer.location,
                order_id=f'TEST-{Order.objects.count() + 1}'
            )
            
            # Verify order was created
            if Order.objects.filter(order_id=order.order_id).exists():
                print(f"✓ Order created successfully: {order.order_id}")
            else:
                print(f"✗ Order creation failed")
            
            # Verify produce quantity was updated
            produce.refresh_from_db()
            if produce.quantity == initial_quantity - order_quantity:
                print(f"✓ Produce quantity updated correctly: {initial_quantity} → {produce.quantity}")
            else:
                print(f"✗ Produce quantity not updated correctly: {produce.quantity} (expected {initial_quantity - order_quantity})")
            
            # Update order status
            order.status = 'confirmed'
            order.save()
            
            # Verify status update
            order.refresh_from_db()
            if order.status == 'confirmed':
                print(f"✓ Order status updated successfully: {order.status}")
            else:
                print(f"✗ Order status update failed")
    except Exception as e:
        print(f"✗ Order creation flow test failed: {e}")
    
    # Test 2: SMS Notification Flow
    print("\n[2/5] Testing SMS Notification Flow...")
    try:
        # Get a template and a farmer
        template = SMSTemplate.objects.filter(template_type='weather').first()
        farmer = Farmer.objects.first()
        
        if not template or not farmer:
            print("✗ Test data not available. Please run create_test_data.py first.")
        else:
            # Create a new SMS message
            message_text = template.template_text.replace('{farmer_name}', farmer.user.first_name)
            message_text = message_text.replace('{location}', farmer.location)
            message_text = message_text.replace('{alert_type}', 'rain')
            message_text = message_text.replace('{date}', 'tomorrow')
            
            sms = SMSMessage.objects.create(
                recipient=farmer.user,
                phone_number=farmer.phone_number,
                message=message_text,
                status='pending'
            )
            
            # Verify SMS was created
            if SMSMessage.objects.filter(id=sms.id).exists():
                print(f"✓ SMS message created successfully")
            else:
                print(f"✗ SMS message creation failed")
            
            # Update SMS status
            sms.status = 'sent'
            sms.save()
            
            # Verify status update
            sms.refresh_from_db()
            if sms.status == 'sent':
                print(f"✓ SMS status updated successfully: {sms.status}")
            else:
                print(f"✗ SMS status update failed")
    except Exception as e:
        print(f"✗ SMS notification flow test failed: {e}")
    
    # Test 3: Weather Alert Flow
    print("\n[3/5] Testing Weather Alert Flow...")
    try:
        # Create a new weather alert
        alert = WeatherAlert.objects.create(
            location='Test Location',
            alert_type='frost',
            severity='high',
            message='Test frost alert for integration testing',
            is_sent=False
        )
        
        # Verify alert was created
        if WeatherAlert.objects.filter(id=alert.id).exists():
            print(f"✓ Weather alert created successfully")
        else:
            print(f"✗ Weather alert creation failed")
        
        # Mark as sent
        alert.is_sent = True
        alert.save()
        
        # Verify status update
        alert.refresh_from_db()
        if alert.is_sent:
            print(f"✓ Weather alert status updated successfully")
        else:
            print(f"✗ Weather alert status update failed")
    except Exception as e:
        print(f"✗ Weather alert flow test failed: {e}")
    
    # Test 4: Price Update Flow
    print("\n[4/5] Testing Price Update Flow...")
    try:
        # Create a new price update
        update = PriceUpdate.objects.create(
            product_name='Test Product',
            market_location='Test Market',
            current_price=10.0,
            previous_price=9.0,
            price_change=1.0,
            unit='kg',
            is_sent=False
        )
        
        # Verify update was created
        if PriceUpdate.objects.filter(id=update.id).exists():
            print(f"✓ Price update created successfully")
        else:
            print(f"✗ Price update creation failed")
        
        # Mark as sent
        update.is_sent = True
        update.save()
        
        # Verify status update
        update.refresh_from_db()
        if update.is_sent:
            print(f"✓ Price update status updated successfully")
        else:
            print(f"✗ Price update status update failed")
    except Exception as e:
        print(f"✗ Price update flow test failed: {e}")
    
    # Test 5: Rating System Flow
    print("\n[5/5] Testing Rating System Flow...")
    try:
        # Get an order
        order = Order.objects.filter(status='delivered').first()
        
        if not order:
            print("✗ Test data not available. Please run create_test_data.py first.")
        else:
            # Create a new rating
            rating = Rating.objects.create(
                order=order,
                rating=4,
                comment='Test rating for integration testing'
            )
            
            # Verify rating was created
            if Rating.objects.filter(id=rating.id).exists():
                print(f"✓ Rating created successfully: {rating.rating}/5")
            else:
                print(f"✗ Rating creation failed")
            
            # Update rating
            rating.rating = 5
            rating.comment = 'Updated test rating'
            rating.save()
            
            # Verify rating update
            rating.refresh_from_db()
            if rating.rating == 5 and rating.comment == 'Updated test rating':
                print(f"✓ Rating updated successfully: {rating.rating}/5")
            else:
                print(f"✗ Rating update failed")
    except Exception as e:
        print(f"✗ Rating system flow test failed: {e}")
    
    print("\n=== Integration Test Summary ===")
    print("The AgriTech prototype has been tested for key integration flows.")
    print("These tests verify that the different components of the system work together correctly.")

if __name__ == "__main__":
    run_integration_tests()
