import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cenro_mgmt.settings')
django.setup()

from accounts.models import User

username = 'CenroAdmin'
password = 'REPLACE_WITH_YOUR_PASSWORD'

try:
    user = User.objects.get(username=username)
    user.set_password(password)
    user.role = User.Role.ADMIN
    user.is_approved = True
    user.is_superuser = True
    user.is_staff = True
    user.save()
    print(f"User '{username}' updated successfully.")
except User.DoesNotExist:
    user = User.objects.create_superuser(username=username, email='', password=password)
    user.role = User.Role.ADMIN
    user.is_approved = True
    user.save()
    print(f"User '{username}' created successfully.")
