#!/usr/bin/env python
import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cenro_mgmt.settings')
django.setup()

from accounts.models import User

# Update admin user
try:
    admin = User.objects.get(username='admin')
    admin.role = 'ADMIN'
    admin.is_approved = True
    admin.is_superuser = True
    admin.is_staff = True
    admin.save()
    print(f"✓ Admin user updated successfully")
    print(f"  Role: {admin.role}")
    print(f"  Approved: {admin.is_approved}")
except User.DoesNotExist:
    print("✗ Admin user not found")
