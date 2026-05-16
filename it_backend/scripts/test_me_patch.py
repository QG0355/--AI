import json
import argparse
import urllib.request
import urllib.error

parser = argparse.ArgumentParser()
parser.add_argument("--token", required=True)
parser.add_argument("--url", default="http://127.0.0.1:8000/api/me/")
args = parser.parse_args()

req = urllib.request.Request(
    args.url,
    data=json.dumps({"name": "测试用户", "gender": "male", "avatar_url": ""}, ensure_ascii=False).encode("utf-8"),
    headers={"Authorization": f"Token {args.token}", "Content-Type": "application/json"},
    method="PATCH",
)

try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        print(resp.status)
        print(resp.read().decode("utf-8"))
except urllib.error.HTTPError as e:
    print(e.code)
    print(e.read().decode("utf-8"))
