# -*- coding: utf-8 -*-
import urllib.request
import json
import sys

# 模拟前端axios发送的请求
url = "http://127.0.0.1:8000/api/login/"

print("=" * 60)
print("测试登录请求（模拟前端axios）")
print("=" * 60)

# 测试不同的用户名密码组合
test_cases = [
    {"username": "student1", "password": "123456"},
    {"username": "student1", "password": "wrongpassword"},
    {"username": "nonexistent", "password": "123456"},
]

for i, data in enumerate(test_cases, 1):
    print(f"\n测试 {i}: {data['username']} / {data['password']}")
    print("-" * 60)
    
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "axios/1.6.0"
            },
            method="POST"
        )

        with urllib.request.urlopen(req, timeout=10) as resp:
            print(f"Status: {resp.status} OK")
            body = resp.read().decode("utf-8")
            result = json.loads(body)
            print(f"Token: {result.get('token', 'N/A')[:20]}...")
            print(f"User: {result.get('user', {}).get('username', 'N/A')}")
            print(f"Role: {result.get('user', {}).get('role', 'N/A')}")

    except urllib.error.HTTPError as e:
        print(f"Status: {e.code} {e.reason}")
        error_body = e.read().decode("utf-8")
        print(f"Error Body: {error_body}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

print("\n" + "=" * 60)
print("结论：后端API正常工作")
print("如果前端仍然400错误，可能是请求格式或CORS问题")
print("=" * 60)
