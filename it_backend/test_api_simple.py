import urllib.request
import json
import ssl

api_key = "sk-yejrmdhdkioqibkiangxahwhzbdxkccajddgyoplwqxyobte"
base_url = "https://api.siliconflow.cn/v1"
model = "deepseek-ai/DeepSeek-V3"

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

print(f"Testing SiliconFlow API with Key: {api_key[:10]}...")
print(f"Model: {model}")

payload = {
    "model": model,
    "messages": [{"role": "user", "content": "Hello"}],
    "max_tokens": 10,
    "stream": False
}

try:
    req = urllib.request.Request(
        f"{base_url}/chat/completions",
        data=json.dumps(payload).encode('utf-8'),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        method="POST"
    )

    with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
        print(f"SUCCESS! Status: {resp.status}")
        body = resp.read().decode('utf-8')
        print(f"Response: {body}")

except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code} {e.reason}")
    print(f"Error Body: {e.read().decode('utf-8')}")
except Exception as e:
    print(f"Error: {str(e)}")
