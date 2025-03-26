#!/usr/bin/env python
import os
import sys
import django
from django.core.management import call_command

# Set up Django environment
sys.path.append('/home/ubuntu/agritech_prototype')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agritech.settings')
django.setup()

def create_test_data():
    """Create sample data for testing the AgriTech prototype."""
    print("=== Creating Test Data for AgriTech Prototype ===")
    
    # Import models
    from django.contrib.auth.models import User
    from marketplace.models import Farmer, Buyer, ProduceCategory, Produce, Order, Rating
    from sms_service.models import SMSMessage, SMSTemplate, WeatherAlert, PriceUpdate
    
    # Create test users
    print("\n[1/5] Creating test users...")
    try:
        # Create admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@agritech.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            print(f"✓ Created admin user: {admin_user.username}")
        else:
            print(f"✓ Admin user already exists: {admin_user.username}")
        
        # Create farmer users
        farmer_data = [
            {'username': 'mohamed', 'first_name': 'Mohamed', 'last_name': 'Ben Ali', 'email': 'mohamed@example.com', 'location': 'Sfax'},
            {'username': 'ahmed', 'first_name': 'Ahmed', 'last_name': 'Trabelsi', 'email': 'ahmed@example.com', 'location': 'Kairouan'},
            {'username': 'fatima', 'first_name': 'Fatima', 'last_name': 'Mansour', 'email': 'fatima@example.com', 'location': 'Sousse'}
        ]
        
        for data in farmer_data:
            user, created = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    'email': data['email'],
                    'first_name': data['first_name'],
                    'last_name': data['last_name']
                }
            )
            if created:
                user.set_password('password123')
                user.save()
                farmer, f_created = Farmer.objects.get_or_create(
                    user=user,
                    defaults={
                        'phone_number': f'+216{9000000 + User.objects.count()}',
                        'location': data['location']
                    }
                )
                print(f"✓ Created farmer: {user.get_full_name()}")
            else:
                print(f"✓ Farmer already exists: {user.get_full_name()}")
        
        # Create buyer users
        buyer_data = [
            {'username': 'salah', 'first_name': 'Salah', 'last_name': 'Mejri', 'email': 'salah@example.com', 'location': 'Tunis'},
            {'username': 'leila', 'first_name': 'Leila', 'last_name': 'Bouzid', 'email': 'leila@example.com', 'location': 'Bizerte'}
        ]
        
        for data in buyer_data:
            user, created = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    'email': data['email'],
                    'first_name': data['first_name'],
                    'last_name': data['last_name']
                }
            )
            if created:
                user.set_password('password123')
                user.save()
                buyer, b_created = Buyer.objects.get_or_create(
                    user=user,
                    defaults={
                        'phone_number': f'+216{8000000 + User.objects.count()}',
                        'location': data['location']
                    }
                )
                print(f"✓ Created buyer: {user.get_full_name()}")
            else:
                print(f"✓ Buyer already exists: {user.get_full_name()}")
    except Exception as e:
        print(f"✗ User creation failed: {e}")
    
    # Create categories
    print("\n[2/5] Creating product categories...")
    try:
        categories = ['Vegetables', 'Fruits', 'Grains', 'Dairy', 'Olives', 'Dates']
        created_categories = []
        
        for cat_name in categories:
            category, created = ProduceCategory.objects.get_or_create(name=cat_name)
            created_categories.append(category)
            if created:
                print(f"✓ Created category: {category.name}")
            else:
                print(f"✓ ProduceCategory already exists: {category.name}")
    except Exception as e:
        print(f"✗ ProduceCategory creation failed: {e}")
    
    # Create produce listings
    print("\n[3/5] Creating produce listings...")
    try:
        farmers = Farmer.objects.all()
        if not farmers:
            print("✗ No farmers found to create produce listings")
        else:
            produce_data = [
                {'title': 'Fresh Olives', 'description': 'High quality olives from Sfax', 'category': 'Olives', 'price': 3.0, 'quantity': 100, 'unit': 'kg'},
                {'title': 'Organic Tomatoes', 'description': 'Pesticide-free tomatoes', 'category': 'Vegetables', 'price': 2.5, 'quantity': 50, 'unit': 'kg'},
                {'title': 'Premium Dates', 'description': 'Sweet and juicy dates', 'category': 'Dates', 'price': 5.0, 'quantity': 30, 'unit': 'kg'},
                {'title': 'Fresh Milk', 'description': 'Farm fresh milk', 'category': 'Dairy', 'price': 1.8, 'quantity': 20, 'unit': 'liter'},
                {'title': 'Wheat Grain', 'description': 'Locally grown wheat', 'category': 'Grains', 'price': 2.0, 'quantity': 200, 'unit': 'kg'}
            ]
            
            for i, data in enumerate(produce_data):
                farmer = farmers[i % len(farmers)]
                category = ProduceCategory.objects.get(name=data['category'])
                
                produce, created = Produce.objects.get_or_create(
                    title=data['title'],
                    farmer=farmer,
                    defaults={
                        'description': data['description'],
                        'category': category,
                        'price_per_unit': data['price'],
                        'quantity': data['quantity'],
                        'unit': data['unit'],
                        'location': farmer.location,
                        'is_available': True
                    }
                )
                
                if created:
                    print(f"✓ Created produce: {produce.title} by {farmer.user.get_full_name()}")
                else:
                    print(f"✓ Produce already exists: {produce.title}")
    except Exception as e:
        print(f"✗ Produce creation failed: {e}")
    
    # Create orders
    print("\n[4/5] Creating sample orders...")
    try:
        buyers = Buyer.objects.all()
        produce_items = Produce.objects.filter(is_available=True)
        
        if not buyers or not produce_items:
            print("✗ No buyers or produce items found to create orders")
        else:
            statuses = ['pending', 'confirmed', 'processing', 'shipped', 'delivered']
            
            for i, buyer in enumerate(buyers):
                for j in range(2):  # 2 orders per buyer
                    produce = produce_items[(i + j) % len(produce_items)]
                    quantity = min(5, produce.quantity)
                    
                    order, created = Order.objects.get_or_create(
                        buyer=buyer,
                        produce=produce,
                        defaults={
                            'quantity': quantity,
                            'unit_price': produce.price_per_unit,
                            'total_price': quantity * produce.price_per_unit,
                            'status': statuses[(i + j) % len(statuses)],
                            'shipping_address': buyer.location,
                            'order_id': f'ORD-{100 + Order.objects.count()}'
                        }
                    )
                    
                    if created:
                        # Update produce quantity
                        produce.quantity -= quantity
                        if produce.quantity <= 0:
                            produce.is_available = False
                        produce.save()
                        
                        print(f"✓ Created order: {order.order_id} by {buyer.user.get_full_name()}")
                        
                        # Add rating for delivered orders
                        if order.status == 'delivered':
                            rating, r_created = Rating.objects.get_or_create(
                                order=order,
                                defaults={
                                    'rating': (i + j) % 5 + 1,  # 1-5 rating
                                    'comment': f"Good quality produce from {produce.farmer.user.get_full_name()}"
                                }
                            )
                            if r_created:
                                print(f"✓ Created rating: {rating.rating}/5 for order {order.order_id}")
                    else:
                        print(f"✓ Order already exists: {order.order_id}")
    except Exception as e:
        print(f"✗ Order creation failed: {e}")
    
    # Create SMS templates and messages
    print("\n[5/5] Creating SMS templates and messages...")
    try:
        # Create SMS templates
        template_data = [
            {'name': 'Weather Alert', 'template_type': 'weather', 'template_text': 'Hello {farmer_name}, weather alert for {location}: {alert_type} expected on {date}.'},
            {'name': 'Price Update', 'template_type': 'price', 'template_text': 'Hello {farmer_name}, current market price for {product} is {price} TND/{unit} in {location}.'},
            {'name': 'Order Confirmation', 'template_type': 'order', 'template_text': 'Hello {farmer_name}, you have a new order #{order_id} for {quantity} {unit} of {product}.'},
            {'name': 'Order Status', 'template_type': 'order', 'template_text': 'Hello {buyer_name}, your order #{order_id} has been {status}. Thank you for using AgriTech!'}
        ]
        
        for data in template_data:
            template, created = SMSTemplate.objects.get_or_create(
                name=data['name'],
                defaults={
                    'template_type': data['template_type'],
                    'template_text': data['template_text']
                }
            )
            
            if created:
                print(f"✓ Created SMS template: {template.name}")
            else:
                print(f"✓ SMS template already exists: {template.name}")
        
        # Create weather alerts
        weather_data = [
            {'location': 'Sfax', 'alert_type': 'rain', 'severity': 'medium', 'message': 'Moderate rainfall expected in Sfax region tomorrow.'},
            {'location': 'Kairouan', 'alert_type': 'heat', 'severity': 'high', 'message': 'High temperatures expected in Kairouan region for the next 3 days.'}
        ]
        
        for data in weather_data:
            alert, created = WeatherAlert.objects.get_or_create(
                location=data['location'],
                alert_type=data['alert_type'],
                defaults={
                    'severity': data['severity'],
                    'message': data['message'],
                    'is_sent': False
                }
            )
            
            if created:
                print(f"✓ Created weather alert: {alert.alert_type} for {alert.location}")
            else:
                print(f"✓ Weather alert already exists: {alert.alert_type} for {alert.location}")
        
        # Create price updates
        price_data = [
            {'product_name': 'Olives', 'market_location': 'Sfax', 'current_price': 3.2, 'previous_price': 3.0, 'unit': 'kg'},
            {'product_name': 'Tomatoes', 'market_location': 'Tunis', 'current_price': 2.3, 'previous_price': 2.5, 'unit': 'kg'},
            {'product_name': 'Dates', 'market_location': 'Kairouan', 'current_price': 5.5, 'previous_price': 5.0, 'unit': 'kg'}
        ]
        
        for data in price_data:
            update, created = PriceUpdate.objects.get_or_create(
                product_name=data['product_name'],
                market_location=data['market_location'],
                defaults={
                    'current_price': data['current_price'],
                    'previous_price': data['previous_price'],
                    'price_change': data['current_price'] - data['previous_price'],
                    'unit': data['unit'],
                    'is_sent': False
                }
            )
            
            if created:
                print(f"✓ Created price update: {update.product_name} at {update.current_price} TND/{update.unit}")
            else:
                print(f"✓ Price update already exists: {update.product_name}")
    except Exception as e:
        print(f"✗ SMS data creation failed: {e}")
    
    print("\n=== Test Data Creation Summary ===")
    print("Sample data has been created for the AgriTech prototype.")
    print("You can now log in with the following credentials:")
    print("Admin: username=admin, password=admin123")
    print("Farmer: username=mohamed, password=password123")
    print("Buyer: username=salah, password=password123")

if __name__ == "__main__":
    create_test_data()
