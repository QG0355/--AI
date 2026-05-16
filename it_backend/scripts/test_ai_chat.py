import json
import argparse
import urllib.request

parser = argparse.ArgumentParser()
parser.add_argument("--token", required=True)
parser.add_argument("--url", default="http://127.0.0.1:8000/api/ai-chat/")
parser.add_argument("--content", default="宿舍灯不亮了怎么办？")
args = parser.parse_args()

req = urllib.request.Request(
    args.url,
    data=json.dumps({"content": args.content}, ensure_ascii=False).encode("utf-8"),
    headers={
        "Authorization": f"Token {args.token}",
        "Content-Type": "application/json",
    },
    method="POST",
)

with urllib.request.urlopen(req, timeout=10) as resp:
    body = resp.read().decode("utf-8")

print(resp.status)
print(body)
