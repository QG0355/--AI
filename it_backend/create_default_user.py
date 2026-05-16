# -*- coding: utf-8 -*-
import os
import sys
import django

sys.path.insert(0, r'C:\BiShe\BiShe\it_backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'it_backend.settings')

django.setup()

from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

User = get_user_model()

username = "student1"
password = "123456"

try:
    user, created = User.objects.get_or_create(
        username=username,
        defaults={'role': 'student', 'is_identity_bound': False}
    )
    user.set_password(password)
    user.save()
    
    if created:
        print("[OK] User created successfully!")
    else:
        print("[OK] User already exists, password reset!")
    
    token, _ = Token.objects.get_or_create(user=user)
    print("\n========================================")
    print("Login credentials:")
    print(f"   Username: {username}")
    print(f"   Password: {password}")
    print(f"   Token: {token.key}")
    print("========================================")
    print("\nPlease login with above credentials!")

except Exception as e:
    print(f"[ERROR] {str(e)}")
    import traceback
    traceback.print_exc()
