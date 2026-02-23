
import urllib.request
import json
import sys
import ssl
import time

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

api_key = "sk-yejrmdhdkioqibkiangxahwhzbdxkccajddgyoplwqxyobte"
base_urls = [
    "https://api.openai.com/v1",  # 官方（国内不通）
    "https://api.chatanywhere.tech/v1", # 常见免费中转
    "https://api.chatanywhere.com.cn/v1",
    "https://api.gpt-api.in/v1",
    "https://api.one-api.com/v1",
]

payload = {
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "Hello"}],
    "max_tokens": 10
}
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

print(f"Testing Key: {api_key[:10]}...")

for base in base_urls:
    url = f"{base}/chat/completions"
    print(f"\n--- Trying: {base} ---")
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers=headers,
            method="POST"
        )
        start = time.time()
        with urllib.request.urlopen(req, context=ctx, timeout=5) as response:
            print(f"SUCCESS! Status: {response.status}")
            print(f"Response: {response.read().decode('utf-8')[:100]}...")
            # 如果成功，把这个有效的 Base URL 打印出来告诉用户
            print(f"\n[FOUND] Valid Base URL: {base}")
            break
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} {e.reason}")
        # 如果是 401，说明 Key 无效；如果是 404，说明路径不对
        if e.code == 401:
            print("Key invalid for this endpoint.")
    except urllib.error.URLError as e:
        print(f"Connection Failed: {e.reason}")
    except Exception as e:
        print(f"Error: {str(e)}")
