import urllib.request
import urllib.error
import json
import time
import os

BASE_URL = "http://127.0.0.1:8000/api"
ADMIN_URL = "http://127.0.0.1:8000/admin/"

SAMPLE_ATTACHMENT = r"c:\BiShe\BiShe\it_backend\media\tickets\1\d83c782281a34a26b6c63200f90acbee.png"

def call_api(path, data=None, token=None, method="POST"):
    url = f"{BASE_URL}/{path.lstrip('/')}"
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = f"Token {token}"
    
    body = json.dumps(data).encode('utf-8') if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        if hasattr(e, 'read'):
            print(f"Error Body: {e.read().decode('utf-8')}")
        raise e

def call_api_with_status(path, data=None, token=None, method="POST"):
    url = f"{BASE_URL}/{path.lstrip('/')}"
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = f"Token {token}"
    body = json.dumps(data).encode('utf-8') if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            raw = resp.read().decode('utf-8')
            payload = json.loads(raw) if raw else None
            return resp.status, payload
    except urllib.error.HTTPError as e:
        raw = e.read().decode('utf-8')
        try:
            payload = json.loads(raw) if raw else None
        except Exception:
            payload = raw
        return e.code, payload

def upload_ticket_attachment(ticket_id: int, file_path: str, token: str):
    if not os.path.exists(file_path):
        raise RuntimeError(f"Attachment file not found: {file_path}")

    url = f"{BASE_URL}/tickets/{ticket_id}/attachments/"
    boundary = "----Boundary7MA4YWxkTrZu0gW"
    filename = os.path.basename(file_path)
    content_type = "image/png" if filename.lower().endswith(".png") else "application/octet-stream"

    with open(file_path, "rb") as f:
        file_bytes = f.read()

    parts = []
    parts.append(f"--{boundary}\r\n".encode("utf-8"))
    parts.append(
        (
            f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
            f"Content-Type: {content_type}\r\n\r\n"
        ).encode("utf-8")
    )
    parts.append(file_bytes)
    parts.append(f"\r\n--{boundary}--\r\n".encode("utf-8"))
    body = b"".join(parts)

    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "Content-Length": str(len(body)),
    }

    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    with urllib.request.urlopen(req) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8"))

def check_admin_page():
    req = urllib.request.Request(ADMIN_URL, method="GET")
    with urllib.request.urlopen(req) as resp:
        final_url = getattr(resp, "url", ADMIN_URL)
        html = resp.read(2048)
        return resp.status, final_url, html[:200]

def test_full_flow():
    ts = int(time.time())
    username = f"flow_user_{ts}"
    password = "password123"
    
    print(f"--- 1. Registering user {username} ---")
    reg_resp = call_api("register/", {"username": username, "password": password})
    print("Register success")
    
    print("--- 2. Logging in ---")
    login_resp = call_api("login/", {"username": username, "password": password})
    token = login_resp['token']
    user_id = login_resp['user']['id']
    print(f"Login success, token: {token[:10]}...")
    
    print("--- 3. Binding Identity as Student ---")
    bind_resp = call_api("bind-identity/", {
        "role": "student",
        "name": f"Test Student {ts}",
        "identity_id": f"ID_{ts}"
    }, token=token)
    print("Bind success")
    
    print("--- 4. Submitting Ticket ---")
    ticket_resp = call_api("tickets/", {
        "title": "Test Ticket Flow",
        "category": "设备故障",
        "priority": "中",
        "description": "Auto generated ticket for flow testing",
        "location": "Test Room 101",
        "contact": "13800138000"
    }, token=token)
    ticket_id = ticket_resp['id']
    print(f"Ticket submitted, ID: {ticket_id}")

    print("--- 4.1 Uploading Attachment (student) ---")
    up_status, up_payload = upload_ticket_attachment(ticket_id, SAMPLE_ATTACHMENT, token)
    if up_status != 201:
        raise RuntimeError(f"Upload attachment failed: {up_status} {up_payload}")
    print("Attachment uploaded")

    print("--- 4.2 Checking Ticket has attachments ---")
    code, t_detail = call_api_with_status(f"tickets/{ticket_id}/", token=token, method="GET")
    if code != 200:
        raise RuntimeError(f"Ticket detail failed: {code} {t_detail}")
    if not (t_detail.get("attachments") and len(t_detail["attachments"]) >= 1):
        raise RuntimeError("Ticket attachments empty")
    print(f"Attachments count: {len(t_detail['attachments'])}")
    
    # --- Auditor Flow ---
    print("\n--- 5. Auditor Review (Approving) ---")
    auditor_login = call_api("login/", {"username": "auditor_test", "password": "123456"})
    auditor_token = auditor_login['token']
    call_api(f"tickets/{ticket_id}/review/", {"decision": "approve"}, token=auditor_token)
    print("Auditor approved ticket")
    
    # --- Maintenance Flow ---
    print("--- 6. Maintenance Take Order ---")
    maint_login = call_api("login/", {"username": "maint_test", "password": "123456"})
    maint_token = maint_login['token']
    call_api(f"tickets/{ticket_id}/handle/", {"type": "assign"}, token=maint_token)
    print("Maintenance took order")

    print("--- 6.1 Student tries to DELETE while repairing (should be blocked) ---")
    del_code, del_payload = call_api_with_status(f"tickets/{ticket_id}/", token=token, method="DELETE")
    if del_code != 400:
        raise RuntimeError(f"Delete protection failed, got {del_code} {del_payload}")
    print("Delete blocked OK")
    
    print("--- 7. Maintenance Finish Order ---")
    call_api(f"tickets/{ticket_id}/handle/", {"type": "finish"}, token=maint_token)
    print("Maintenance finished order")
    
    # --- Student Flow Final ---
    print("--- 8. Student Evaluate ---")
    call_api(f"tickets/{ticket_id}/handle/", {
        "type": "evaluate",
        "rating": 5,
        "evaluation": "Excellent service!",
        "is_anonymous": False
    }, token=token)
    print("Student evaluated. Flow complete!")

    print("\n--- 9. AI Chat should call DeepSeek (llm mode) ---")
    ai_code, ai_payload = call_api_with_status("ai-chat/", {"content": "空调不制冷怎么办？"}, token=token, method="POST")
    if ai_code != 200:
        raise RuntimeError(f"AI call failed: {ai_code} {ai_payload}")
    if ai_payload.get("mode") != "llm":
        raise RuntimeError(f"AI not in llm mode: {ai_payload.get('mode')}")
    if not ai_payload.get("ai_enabled"):
        raise RuntimeError("AI not enabled")
    print("AI OK (llm)")

    print("\n--- 10. Django Admin page reachable ---")
    st, final_url, _ = check_admin_page()
    if st not in (200, 302):
        raise RuntimeError(f"Admin page status unexpected: {st}")
    print(f"Admin reachable: {final_url}")

if __name__ == "__main__":
    try:
        test_full_flow()
        print("\n[SUCCESS] Entire project flow verified successfully!")
    except Exception as e:
        print(f"\n[FAILED] Flow verification failed: {e}")
