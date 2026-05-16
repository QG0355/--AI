# -*- coding: utf-8 -*-
import os
import sys
import django

sys.path.insert(0, r'C:\BiShe\BiShe\it_backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'it_backend.settings')

os.environ['AI_API_KEY'] = 'sk-yejrmdhdkioqibkiangxahwhzbdxkccajddgyoplwqxyobte'
os.environ['AI_BASE_URL'] = 'https://api.siliconflow.cn/v1'
os.environ['AI_MODEL'] = 'deepseek-ai/DeepSeek-V3'
os.environ['AI_TIMEOUT'] = '20'

django.setup()

from tickets_api.views import ai_chat
from django.test import RequestFactory
from rest_framework.authtoken.models import Token
import json

factory = RequestFactory()

try:
    user = None
    token = None
    
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.filter(role='student').first()
        if user:
            token = Token.objects.get(user=user)
            print(f"Found student user: {user.username}")
    except Exception as e:
        print(f"Error finding user: {e}")

    if not user:
        user = User.objects.first()
        if user:
            token = Token.objects.get(user=user)
            print(f"Using first user: {user.username}")

    if user and token:
        request = factory.post(
            '/api/ai-chat/',
            data=json.dumps({'content': '宿舍灯不亮了怎么办？'}),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Token {token.key}'
        )
        request.user = user
        
        print(f"Testing AI chat with user: {user.username}, token: {token.key[:10]}...")
        
        response = ai_chat(request)
        print(f"Status: {response.status_code}")
        
        response.render()
        if hasattr(response, 'content'):
            result = json.loads(response.content)
            print(f"Response: {json.dumps(result, ensure_ascii=False, indent=2)}")
    else:
        print("No user/token found. Creating a test user...")
        
except Exception as e:
    print(f"Error: {str(e)}")
    import traceback
    traceback.print_exc()
