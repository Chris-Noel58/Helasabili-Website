#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nchskikuyu.settings')
django.setup()

from django.contrib.auth.models import User

# Create admin user
user, created = User.objects.update_or_create(
    username='admin',
    defaults={
        'email': 'admin@nchsm.ac.ke',
        'is_staff': True,
        'is_superuser': True,
    }
)

user.set_password('admin123')
user.save()

if created:
    print("✓ Admin user created successfully")
else:
    print("✓ Admin user updated successfully")
