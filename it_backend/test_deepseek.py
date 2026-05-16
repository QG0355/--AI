import urllib.request
import json
import ssl
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ.get('AI_API_KEY')
BASE_URL = os.environ.get('AI_BASE_URL', 'https://api.deepseek.com/v1')
MODEL = os.environ.get('AI_MODEL', 'deepseek-chat')

print(f"Testing DeepSeek API...")
print(f"URL: {BASE_URL}/chat/completions")
print(f"Model: {MODEL}")
print(f"Key: {API_KEY[:15]}...")

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

payload = {
    "model": MODEL,
    "messages": [
        {"role": "system", "content": "你是校园报修AI助手，只能提供报修建议，不能进行带电操作指导。"},
        {"role": "user", "content": "空调不制冷怎么办？"}
    ],
    "temperature": 0.2,
}

req = urllib.request.Request(
    f"{BASE_URL}/chat/completions",
    data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
    headers={
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    },
    method="POST",
)

try:
    with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        answer = data['choices'][0]['message']['content']
        print(f"\n[OK] DeepSeek API Works!")
        print(f"Response:\n{answer}")
except urllib.request.HTTPError as e:
    error_body = e.read().decode('utf-8')
    print(f"\n[HTTP Error {e.code}] {error_body}")
except Exception as e:
    print(f"\n[Error] {e}")
