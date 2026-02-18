#!/usr/bin/env python
"""
Setup script for CENRO Admin System
Initializes required data and models
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cenro_mgmt.settings')
django.setup()

from django.contrib.auth import get_user_model
from decimal import Decimal
from dashboard.models import ChargeCategory, MembershipRecord
from accounts.models import User

def setup_admin_system():
    """Initialize admin system with required data"""
    
    print("🚀 Setting up CENRO Admin System...\n")
    
    # 1. Create charge categories
    print("1️⃣  Creating charge categories...")
    categories = [
        {
            'category': 'RESIDENTIAL',
            'base_rate': Decimal('100.00'),
            'description': 'Residential property septage declogging service charges'
        },
        {
            'category': 'COMMERCIAL',
            'base_rate': Decimal('150.00'),
            'description': 'Commercial property septage declogging service charges'
        }
    ]
    
    for cat in categories:
        obj, created = ChargeCategory.objects.get_or_create(
            category=cat['category'],
            defaults={'base_rate': cat['base_rate'], 'description': cat['description']}
        )
        status = "✓ Created" if created else "✓ Exists"
        print(f"   {status}: {cat['category']}")
    
    # 2. Create admin user if not exists
    print("\n2️⃣  Checking admin user...")
    try:
        admin_user = User.objects.get(username='admin')
        admin_user.role = User.Role.ADMIN
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.is_approved = True
        admin_user.save()
        print("   ✓ Admin user updated")
    except User.DoesNotExist:
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@cenro.local',
            password='admin123'
        )
        admin_user.role = User.Role.ADMIN
        admin_user.is_approved = True
        admin_user.save()
        print("   ✓ Admin user created")
    
    # 3. Create sample staff users
    print("\n3️⃣  Setting up staff users...")
    staff_data = [
        {'username': 'staff1', 'first_name': 'Juan', 'last_name': 'Dela Cruz'},
        {'username': 'staff2', 'first_name': 'Maria', 'last_name': 'Santos'},
    ]
    
    for staff in staff_data:
        try:
            user = User.objects.get(username=staff['username'])
            status = "exists"
        except User.DoesNotExist:
            user = User.objects.create_user(
                username=staff['username'],
                email=f"{staff['username']}@cenro.local",
                password=f"{staff['username']}123",
                first_name=staff['first_name'],
                last_name=staff['last_name']
            )
            user.role = User.Role.STAFF
            user.is_approved = True
            user.is_staff = True
            user.save()
            status = "created"
        print(f"   ✓ {staff['username']}: {status}")
    
    # 4. Create sample consumer users
    print("\n4️⃣  Setting up consumer users...")
    from accounts.models import ConsumerProfile
    
    consumer_data = [
        {
            'username': 'consumer1',
            'first_name': 'Jose',
            'last_name': 'Garcia',
            'barangay': 'Poblacion',
            'address': '123 Main St, Bayawan'
        },
        {
            'username': 'consumer2',
            'first_name': 'Rosa',
            'last_name': 'Lopez',
            'barangay': 'San Jose',
            'address': '456 Oak Ave, Bayawan'
        },
    ]
    
    for cons in consumer_data:
        try:
            user = User.objects.get(username=cons['username'])
            status = "exists"
        except User.DoesNotExist:
            user = User.objects.create_user(
                username=cons['username'],
                email=f"{cons['username']}@consumers.local",
                password=f"{cons['username']}123",
                first_name=cons['first_name'],
                last_name=cons['last_name']
            )
            user.role = User.Role.CONSUMER
            user.is_approved = True
            user.save()
            
            ConsumerProfile.objects.create(
                user=user,
                barangay=cons['barangay'],
                address=cons['address']
            )
            status = "created"
        print(f"   ✓ {cons['username']}: {status}")
    
    # 5. Create membership records
    print("\n5️⃣  Creating membership records...")
    consumers = User.objects.filter(role=User.Role.CONSUMER)
    for consumer in consumers:
        obj, created = MembershipRecord.objects.get_or_create(
            user=consumer,
            defaults={
                'total_paid': Decimal('0.00'),
                'total_free': Decimal('0.00'),
                'remaining_balance': Decimal('0.00'),
                'is_active': True
            }
        )
        status = "✓ Created" if created else "✓ Exists"
        print(f"   {status}: {consumer.get_full_name()}")
    
    print("\n" + "="*50)
    print("✅ Admin System Setup Complete!")
    print("="*50)
    print("\n📋 Default Credentials:")
    print("   Admin:      admin / admin123")
    print("   Staff 1:    staff1 / staff1123")
    print("   Staff 2:    staff2 / staff2123")
    print("   Consumer 1: consumer1 / consumer1123")
    print("   Consumer 2: consumer2 / consumer2123")
    print("\n🌐 Access Points:")
    print("   Home:      http://127.0.0.1:8000/")
    print("   Login:     http://127.0.0.1:8000/accounts/login/")
    print("   Admin:     http://127.0.0.1:8000/dashboard/admin/")
    print("   Services:  http://127.0.0.1:8000/services/")
    print("\n✨ System is ready for use!")

if __name__ == '__main__':
    try:
        setup_admin_system()
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)
