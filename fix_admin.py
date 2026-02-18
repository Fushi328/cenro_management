import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cenro_mgmt.settings')
django.setup()

from accounts.models import User

admin = User.objects.get(username='admin')
admin.role = User.Role.ADMIN
admin.is_approved = True
admin.is_superuser = True
admin.is_staff = True
admin.save()

print(f"Admin user fixed:")
print(f"  Username: {admin.username}")
print(f"  Role: {admin.role}")
print(f"  Is Approved: {admin.is_approved}")
print(f"  Is Superuser: {admin.is_superuser}")
print(f"  Is Staff: {admin.is_staff}")
