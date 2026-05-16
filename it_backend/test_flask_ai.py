import urllib.request
import json

try:
    # Test health
    with urllib.request.urlopen('http://localhost:5000/health') as resp:
        health = json.loads(resp.read().decode('utf-8'))
        print("Flask Health:", json.dumps(health, indent=2, ensure_ascii=False))
    
    # Test chat
    chat_data = json.dumps({"content": "空调不制冷怎么办？"}).encode('utf-8')
    chat_req = urllib.request.Request(
        'http://localhost:5000/chat',
        data=chat_data,
        headers={'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(chat_req, timeout=30) as resp:
        result = json.loads(resp.read().decode('utf-8'))
        print("\nFlask Chat Result:")
        print(f"  ai_connected: {result.get('ai_connected')}")
        print(f"  error: {result.get('error')}")
        print(f"  answer: {result.get('answer', '')[:150]}...")
except Exception as e:
    print(f"Error: {e}")
