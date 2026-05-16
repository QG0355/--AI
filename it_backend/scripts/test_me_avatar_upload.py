import argparse
import uuid
import urllib.request
import urllib.error

PNG_1X1 = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc`\x00"
    b"\x00\x00\x02\x00\x01\xe2!\xbc3\x00\x00\x00\x00IEND\xaeB`\x82"
)

parser = argparse.ArgumentParser()
parser.add_argument("--token", required=True)
parser.add_argument("--url", default="http://127.0.0.1:8000/api/me/avatar/")
args = parser.parse_args()

boundary = f"----WebKitFormBoundary{uuid.uuid4().hex}".encode("ascii")
crlf = b"\r\n"

body = b""
body += b"--" + boundary + crlf
body += b'Content-Disposition: form-data; name="file"; filename="avatar.png"' + crlf
body += b"Content-Type: image/png" + crlf
body += crlf
body += PNG_1X1 + crlf
body += b"--" + boundary + b"--" + crlf

req = urllib.request.Request(
    args.url,
    data=body,
    headers={
        "Authorization": f"Token {args.token}",
        "Content-Type": f"multipart/form-data; boundary={boundary.decode('ascii')}",
    },
    method="POST",
)

try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        print(resp.status)
        print(resp.read().decode("utf-8"))
except urllib.error.HTTPError as e:
    print(e.code)
    print(e.read().decode("utf-8"))
