import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'it_backend.settings')
sys.path.append('it_backend')
django.setup()

from tickets_api.models import AiSetting
import urllib.request
import json

obj, _ = AiSetting.objects.get_or_create(id=1)
obj.api_key = 'sk-0fd8243a9edd4793b22f1f9be0568f07'
obj.api_base_url = 'https://dashscope.aliyuncs.com/compatible-mode/v1'
obj.api_model = 'qwen-turbo'
obj.api_model_deep = 'qwen-plus'
obj.llm_enabled = True
obj.save()

headers = {
    'Authorization': f'Bearer {obj.api_key}',
    'Content-Type': 'application/json'
}
data = {
    'model': obj.api_model,
    'messages': [{'role': 'user', 'content': '你好，测试一下'}],
    'max_tokens': 50
}

req = urllib.request.Request(
    f'{obj.api_base_url}/chat/completions',
    headers=headers,
    data=json.dumps(data).encode('utf-8'),
    method='POST'
)

try:
    with urllib.request.urlopen(req) as response:
        print('API Status Code:', response.status)
        print('API Response:', json.loads(response.read().decode('utf-8')))
except Exception as e:
    print('API Error:', e)
