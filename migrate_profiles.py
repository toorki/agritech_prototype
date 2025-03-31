import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agritech.settings')  # Replace with your actual settings module
django.setup()

from django.contrib.auth.models import User
from marketplace.models import UserProfile, Farmer, Sponsor, Buyer

# Dictionary to map instance IDs to usernames (adjust these based on your data)
user_mappings = {
    1: 'salah_farmer',   # Existing farmer
    2: 'salah_farmer',   # Existing farmer
    3: 'mohamed_farmer2', # New farmer
    4: 'ahmed_farmer2',   # New farmer
    5: 'ali_sponsor',    # Existing sponsor
    6: 'ali_sponsor',    # Existing sponsor
    7: 'hassan_sponsor2', # New sponsor
    8: 'salah_buyer',    # Existing buyer
    9: 'salah_buyer',    # Existing buyer
    10: 'fatma_buyer2',  # New buyer
}

# Migrate existing farmers
for farmer in Farmer.objects.all():
    if farmer.profile_id is None:
        username = user_mappings.get(farmer.id)
        if username:
            try:
                user = User.objects.get(username=username)
                profile, created = UserProfile.objects.get_or_create(user=user, defaults={'role': 'farmer'})
                if not created:
                    print(f"Warning: UserProfile already exists for {username}, reusing it")
                farmer.profile = profile
                farmer.save()
                print(f"Successfully linked farmer {farmer.id} to profile for {username}")
            except User.DoesNotExist:
                print(f"Warning: User {username} not found for farmer {farmer.id}")
        else:
            print(f"Warning: No username mapping found for farmer {farmer.id}. Manual assignment needed.")

# Migrate existing sponsors
for sponsor in Sponsor.objects.all():
    if sponsor.profile_id is None:
        username = user_mappings.get(sponsor.id)
        if username:
            try:
                user = User.objects.get(username=username)
                profile, created = UserProfile.objects.get_or_create(user=user, defaults={'role': 'sponsor'})
                if not created:
                    print(f"Warning: UserProfile already exists for {username}, reusing it")
                sponsor.profile = profile
                sponsor.save()
                print(f"Successfully linked sponsor {sponsor.id} to profile for {username}")
            except User.DoesNotExist:
                print(f"Warning: User {username} not found for sponsor {sponsor.id}")
        else:
            print(f"Warning: No username mapping found for sponsor {sponsor.id}. Manual assignment needed.")

# Migrate existing buyers
for buyer in Buyer.objects.all():
    if buyer.profile_id is None:
        username = user_mappings.get(buyer.id)
        if username:
            try:
                user = User.objects.get(username=username)
                profile, created = UserProfile.objects.get_or_create(user=user, defaults={'role': 'buyer'})
                if not created:
                    print(f"Warning: UserProfile already exists for {username}, reusing it")
                buyer.profile = profile
                buyer.save()
                print(f"Successfully linked buyer {buyer.id} to profile for {username}")
            except User.DoesNotExist:
                print(f"Warning: User {username} not found for buyer {buyer.id}")
        else:
            print(f"Warning: No username mapping found for buyer {buyer.id}. Manual assignment needed.")