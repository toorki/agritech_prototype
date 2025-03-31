import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agritech.settings')
django.setup()

from django.contrib.auth.models import User

users = User.objects.all()
print("Existing users in database:")
for user in users:
    print(f"User: {user.username}")