from django.contrib.auth.models import User
users = ['salah_farmer', 'ahmed_sponsor', 'jihad_sponsor', 'houssem_sponsor']
for username in users:
    user = User.objects.get(username=username)
    user.set_password('password123')
    user.save()