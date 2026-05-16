# -*- coding: utf-8 -*-
import urllib.request
import json
import ssl

url = "http://127.0.0.1:5000/ai-chat/"
data = {
    "content": "宿舍灯不亮了怎么办？"
}

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

try:
    req = urllib.request.Request(
        url,
        data=json.dumps(data, ensure_ascii=False).encode("utf-8"),
        headers={
            "Content-Type": "application/json"
        },
        method="POST"
    )

    with urllib.request.urlopen(req, context=ctx, timeout=20) as resp:
        print(f"Status: {resp.status}")
        body = resp.read().decode("utf-8")
        result = json.loads(body)
        print(f"Response: {json.dumps(result, ensure_ascii=False, indent=2)}")

except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code} {e.reason}")
    print(f"Error Body: {e.read().decode('utf-8')}")
except Exception as e:
    print(f"Error: {str(e)}")
