import urllib.request
import json
import os

BASE_URL = "http://127.0.0.1:8000/api"

# 先登录获取token
login_data = json.dumps({"username": "student1", "password": "123456"}).encode('utf-8')
login_req = urllib.request.Request(
    f"{BASE_URL}/login/",
    data=login_data,
    headers={'Content-Type': 'application/json'}
)
with urllib.request.urlopen(login_req) as resp:
    login_resp = json.loads(resp.read().decode('utf-8'))
    token = login_resp['token']
    print(f"Logged in as: {login_resp['user']['username']}")

# 测试AI聊天
chat_data = json.dumps({"content": "空调不制冷怎么办？"}).encode('utf-8')
chat_req = urllib.request.Request(
    f"{BASE_URL}/ai-chat/",
    data=chat_data,
    headers={
        'Content-Type': 'application/json',
        'Authorization': f'Token {token}'
    }
)

try:
    with urllib.request.urlopen(chat_req, timeout=30) as resp:
        chat_resp = json.loads(resp.read().decode('utf-8'))
        print(f"\nMode: {chat_resp.get('mode')}")
        print(f"AI Enabled: {chat_resp.get('ai_enabled')}")
        print(f"\nAnswer preview:\n{chat_resp.get('answer', '')[:300]}...")
        
        if chat_resp.get('mode') == 'fallback' and not chat_resp.get('ai_enabled'):
            print("\n[ISSUE] AI is NOT connected. Using built-in template responses.")
            print("       SiliconFlow API key may be missing or invalid.")
            print(f"\nEnvironment variables check:")
            print(f"  AI_API_KEY: {'***' if os.environ.get('AI_API_KEY') else 'NOT SET'}")
            print(f"  OPENAI_API_KEY: {'***' if os.environ.get('OPENAI_API_KEY') else 'NOT SET'}")
        elif chat_resp.get('mode') == 'llm':
            print("\n[OK] AI is properly connected!")
except Exception as e:
    print(f"\nError: {e}")
