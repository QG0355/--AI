# -*- coding: utf-8 -*-
import urllib.request
import json
import random
import string

def random_string(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

url = "http://127.0.0.1:8000/api/register/"
username = f"user_{random_string()}"
password = "test_password123"

data = {
    "username": username,
    "password": password
}

print(f"Testing Registration API...")
print(f"URL: {url}")
print(f"Payload: {json.dumps(data)}")

try:
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Origin": "http://localhost:5176"
        },
        method="POST"
    )

    with urllib.request.urlopen(req, timeout=10) as resp:
        print(f"\nStatus: {resp.status}")
        body = resp.read().decode("utf-8")
        result = json.loads(body)
        print(f"Response: {json.dumps(result, ensure_ascii=False, indent=2)}")
        print(f"\n[OK] Registration successful for {username}!")

except urllib.error.HTTPError as e:
    print(f"\nHTTP Error: {e.code} {e.reason}")
    error_body = e.read().decode("utf-8")
    print(f"Error Body: {error_body}")
except Exception as e:
    print(f"\nError: {str(e)}")
