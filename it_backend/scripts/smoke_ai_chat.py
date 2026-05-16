import json
import urllib.request
import urllib.error

BASE = "http://127.0.0.1:8000/api"

def req(method, url, data=None, headers=None):
    if data is not None and not isinstance(data, (bytes, bytearray)):
        data = json.dumps(data, ensure_ascii=False).encode("utf-8")
        headers = {"Content-Type": "application/json", **(headers or {})}
    req = urllib.request.Request(url, data=data, headers=headers or {}, method=method)
    with urllib.request.urlopen(req, timeout=10) as resp:
        body = resp.read().decode("utf-8")
        return resp.status, body

def main():
    # 1) register
    try:
        status, body = req("POST", f"{BASE}/register/", {"username": "smoke_user", "password": "123456"})
        print("register:", status, body)
    except urllib.error.HTTPError as e:
        print("register error:", e.code, e.read().decode("utf-8"))

    # 2) login
    status, body = req("POST", f"{BASE}/login/", {"username": "smoke_user", "password": "123456"})
    print("login:", status, body)
    token = json.loads(body)["token"]

    # 3) ai-chat
    status, body = req(
        "POST",
        f"{BASE}/ai-chat/",
        {"content": "宿舍断网了，怎么处理？"},
        headers={"Authorization": f"Token {token}"},
    )
    print("ai-chat:", status, body)
    data = json.loads(body)
    print("diagnosis:", {"mode": data.get("mode"), "ai_enabled": data.get("ai_enabled"), "warning": data.get("warning")})

if __name__ == "__main__":
    main()
