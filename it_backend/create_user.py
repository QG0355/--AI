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

username = input("请输入用户名: ").strip()
password = input("请输入密码: ").strip()

if not username or not password:
    print("用户名和密码不能为空")
    sys.exit(1)

try:
    user, created = User.objects.get_or_create(
        username=username,
        defaults={'role': 'student'}
    )
    user.set_password(password)
    user.save()
    
    if created:
        print(f"✅ 用户 {username} 创建成功！")
    else:
        print(f"✅ 用户 {username} 密码已更新！")
    
    token, _ = Token.objects.get_or_create(user=user)
    print(f"\nToken: {token.key}")
    print(f"\n登录测试:")
    print(f"用户名: {username}")
    print(f"密码: {password}")

except Exception as e:
    print(f"❌ 错误: {str(e)}")
    import traceback
    traceback.print_exc()
