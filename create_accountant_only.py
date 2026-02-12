"""
Create only accountant user

Run this script:
python create_accountant_only.py
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Database1.settings')
django.setup()

from accounts.models import CustomUser
from django.db import IntegrityError

def create_accountant():
    """Create only accountant user"""
    
    print("Creating accountant user...\n")
    
    accountant_data = {
        'username': 'accountant',
        'email': 'accountant@school.edu',
        'password': 'accountant123',
        'first_name': 'Omar',
        'last_name': 'Al-Farouk',
        'role': 'accountant',
        'employee_id': 'ACC001',
        'department': 'Finance',
        'is_staff': False,
        'is_superuser': False,
    }
    
    try:
        # Check if accountant already exists
        if CustomUser.objects.filter(username=accountant_data['username']).exists():
            print(f"⏭️  Accountant already exists")
            existing_user = CustomUser.objects.get(username=accountant_data['username'])
            print(f"\nExisting Accountant Details:")
            print(f"  • Username: {existing_user.username}")
            print(f"  • Email: {existing_user.email}")
            print(f"  • Name: {existing_user.get_full_name()}")
            print(f"  • Role: {existing_user.get_role_display()}")
            print(f"  • Employee ID: {existing_user.employee_id}")
            print(f"  • Department: {existing_user.department}")
            return
        
        # Extract password
        password = accountant_data.pop('password')
        
        # Create accountant user
        user = CustomUser.objects.create_user(**accountant_data)
        user.set_password(password)
        user.save()
        
        print(f"✅ Created: {user.username} ({user.get_role_display()})")
        
        print(f"\n{'='*60}")
        print(f"✅ Accountant user created successfully!")
        print(f"{'='*60}\n")
        
        print(f"📋 LOGIN CREDENTIALS")
        print(f"{'='*60}\n")
        
        print("Role: Accountant (Billing, Reports)")
        print(f"  Username: {user.username}")
        print(f"  Password: {password}")
        print(f"  Email: {user.email}")
        print(f"  Name: {user.get_full_name()}")
        print(f"  Employee ID: {user.employee_id}")
        print(f"  Department: {user.department}\n")
        
        print(f"{'='*60}")
        print(f"🌐 Access the application at: http://127.0.0.1:8001/accounts/login/")
        print(f"{'='*60}\n")
        
    except IntegrityError as e:
        print(f"❌ Error creating accountant: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


if __name__ == '__main__':
    create_accountant()
