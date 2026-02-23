
import urllib.request
import json
import sys
import ssl

# 忽略 SSL 证书验证（防止本地环境证书问题）
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

api_key = "sk-yejrmdhdkioqibkiangxahwhzbdxkccajddgyoplwqxyobte"
# 先试官方地址，如果用户没给 Base URL
base_urls = [
    "https://api.openai.com/v1/chat/completions",
    # 这里可以列出一些常见的国内转发地址试试，但为了准确，主要测连通性
    # 比如 "https://api.chatanywhere.tech/v1/chat/completions" (常见免费)
    # 但不知道用户买的是哪家的
]

url = "https://api.openai.com/v1/chat/completions"

payload = {
    "model": "gpt-3.5-turbo", # 先试个最通用的
    "messages": [{"role": "user", "content": "Hello"}],
    "max_tokens": 10
}

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

print(f"Testing API Key: {api_key[:10]}***")
print(f"Target URL: {url}")

try:
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode('utf-8'),
        headers=headers,
        method="POST"
    )
    with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
        print(f"Status: {response.status}")
        print(f"Response: {response.read().decode('utf-8')}")
except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code} {e.reason}")
    print(f"Error Body: {e.read().decode('utf-8')}")
except urllib.error.URLError as e:
    print(f"URL Error: {e.reason}")
    print("Hint: 如果是 Connection timed out 或拒绝连接，说明国内网络连不上 api.openai.com，你需要向卖家索要 'API 接口地址(Base URL)'")
except Exception as e:
    print(f"Error: {str(e)}")
