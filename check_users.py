#!/usr/bin/env python
"""Script to check all user accounts in the database"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carmodx.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

print("\n" + "="*60)
print("USER ACCOUNTS IN DATABASE")
print("="*60 + "\n")

users = User.objects.all()

if not users.exists():
    print("No users found in the database.\n")
else:
    for user in users:
        print(f"Username: {user.username}")
        print(f"Email: {user.email}")
        print(f"Role: ", end="")
        if user.is_superuser:
            print("ADMIN (Superuser)")
        elif user.is_staff:
            print("STAFF/EMPLOYEE")
        else:
            print("CUSTOMER")
        print(f"Active: {user.is_active}")
        print("-" * 60)

print("\nNOTE: Passwords are encrypted and cannot be displayed.")
print("If you need to reset a password, use: python manage.py changepassword <username>")
print("\n")
