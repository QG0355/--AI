import argparse
import urllib.request

parser = argparse.ArgumentParser()
parser.add_argument("--token", required=True)
parser.add_argument("--url", default="http://127.0.0.1:8000/api/me/")
args = parser.parse_args()

req = urllib.request.Request(
    args.url,
    headers={"Authorization": f"Token {args.token}"},
    method="GET",
)

with urllib.request.urlopen(req, timeout=10) as resp:
    print(resp.status)
    print(resp.read().decode("utf-8"))
