import urllib.request
import json
import time

BASE_URL = "http://127.0.0.1:8000/api"

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

if __name__ == "__main__":
    try:
        test_full_flow()
        print("\n[SUCCESS] Entire project flow verified successfully!")
    except Exception as e:
        print(f"\n[FAILED] Flow verification failed: {e}")
