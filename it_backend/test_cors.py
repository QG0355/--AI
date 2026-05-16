# -*- coding: utf-8 -*-
import urllib.request
import json

test_urls = [
    "http://127.0.0.1:8000/api/login/",
    "http://localhost:8000/api/login/",
    "http://127.0.0.1:8000/admin/",
]

data = {
    "username": "student1",
    "password": "123456"
}

for url in test_urls:
    print(f"\nTesting: {url}")
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Origin": "http://localhost:5176"
            },
            method="POST"
        )

        with urllib.request.urlopen(req, timeout=5) as resp:
            print(f"Status: {resp.status}")
            print(f"CORS Headers: {dict(resp.headers)}")
            body = resp.read().decode("utf-8")
            result = json.loads(body)
            print(f"Response: {json.dumps(result, ensure_ascii=False, indent=2)}")

    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} {e.reason}")
        print(f"Headers: {dict(e.headers)}")
    except Exception as e:
        print(f"Error: {str(e)}")
