# -*- coding: utf-8 -*-
import urllib.request
import json

url = "http://127.0.0.1:8000/api/login/"
data = {
    "username": "student1",
    "password": "123456"
}

try:
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers={
            "Content-Type": "application/json"
        },
        method="POST"
    )

    with urllib.request.urlopen(req, timeout=10) as resp:
        print("Status:", resp.status)
        body = resp.read().decode("utf-8")
        result = json.loads(body)
        print("Response:", json.dumps(result, ensure_ascii=False, indent=2))
        print("\n[OK] Login successful!")

except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code} {e.reason}")
    print(f"Error Body: {e.read().decode('utf-8')}")
except Exception as e:
    print(f"Error: {str(e)}")
