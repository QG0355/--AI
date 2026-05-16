# -*- coding: utf-8 -*-
import urllib.request
import json

url = "http://127.0.0.1:8000/api/login/"
data = {
    "username": "student1",
    "password": "123456"
}

print("Testing login API...")
print(f"URL: {url}")
print(f"Data: {json.dumps(data)}")

try:
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json"
        },
        method="POST"
    )

    with urllib.request.urlopen(req, timeout=10) as resp:
        print(f"\nStatus: {resp.status}")
        body = resp.read().decode("utf-8")
        result = json.loads(body)
        print(f"Response: {json.dumps(result, ensure_ascii=False, indent=2)}")
        print("\n[OK] Login successful!")

except urllib.error.HTTPError as e:
    print(f"\nHTTP Error: {e.code} {e.reason}")
    error_body = e.read().decode("utf-8")
    print(f"Error Body: {error_body}")
    
    # 尝试解析JSON
    try:
        error_json = json.loads(error_body)
        print(f"Parsed Error: {json.dumps(error_json, ensure_ascii=False, indent=2)}")
    except:
        pass
        
except Exception as e:
    print(f"\nError: {str(e)}")
