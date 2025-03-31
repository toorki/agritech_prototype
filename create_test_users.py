import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agritech.settings')
django.setup()

from django.contrib.auth.models import User
from marketplace.models import UserProfile, Farmer, Sponsor, Buyer

# Create additional farmers
farmer_users = [
    {'username': 'mohamed_farmer2', 'password': 'password123', 'name': 'Mohamed', 'location': 'Kairouan'},
    {'username': 'ahmed_farmer2', 'password': 'password123', 'name': 'Ahmed', 'location': 'Sfax'},
    {'username': 'ali_farmer2', 'password': 'password123', 'name': 'Ali', 'location': 'Tunis'},
]

for data in farmer_users:
    user, created = User.objects.get_or_create(username=data['username'], defaults={'password': data['password']})
    if not created:
        user.set_password(data['password'])  # Update password if user exists
        user.save()
    profile, created = UserProfile.objects.get_or_create(user=user)
    if created:
        profile.role = 'farmer'
        profile.save()
    else:
        print(f"Warning: UserProfile already exists for {data['username']}, ensuring role is 'farmer'")
        if profile.role != 'farmer':
            profile.role = 'farmer'
            profile.save()
    Farmer.objects.create(profile=profile, phone_number=f'12{len(farmer_users)}4567890', location=data['location'])

# Create additional sponsors
sponsor_users = [
    {'username': 'hassan_sponsor2', 'password': 'password123', 'organization': 'AgriFund'},
    {'username': 'youssef_sponsor2', 'password': 'password123', 'organization': 'GreenGrowth'},
]

for data in sponsor_users:
    user, created = User.objects.get_or_create(username=data['username'], defaults={'password': data['password']})
    if not created:
        user.set_password(data['password'])  # Update password if user exists
        user.save()
    profile, created = UserProfile.objects.get_or_create(user=user)
    if created:
        profile.role = 'sponsor'
        profile.save()
    else:
        print(f"Warning: UserProfile already exists for {data['username']}, ensuring role is 'sponsor'")
        if profile.role != 'sponsor':
            profile.role = 'sponsor'
            profile.save()
    Sponsor.objects.create(profile=profile, phone_number=f'12{len(sponsor_users)}7654321', organization=data['organization'])

# Create additional buyers
buyer_users = [
    {'username': 'fatma_buyer2', 'password': 'password123', 'location': 'Sousse'},
    {'username': 'khalil_buyer2', 'password': 'password123', 'location': 'Bizerte'},
]

for data in buyer_users:
    user, created = User.objects.get_or_create(username=data['username'], defaults={'password': data['password']})
    if not created:
        user.set_password(data['password'])  # Update password if user exists
        user.save()
    profile, created = UserProfile.objects.get_or_create(user=user)
    if created:
        profile.role = 'buyer'
        profile.save()
    else:
        print(f"Warning: UserProfile already exists for {data['username']}, ensuring role is 'buyer'")
        if profile.role != 'buyer':
            profile.role = 'buyer'
            profile.save()
    Buyer.objects.create(profile=profile, phone_number=f'12{len(buyer_users)}6543210', location=data['location'])

print("Successfully created additional farmers, sponsors, and buyers!")