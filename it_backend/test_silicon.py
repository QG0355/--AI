
import urllib.request
import json
import ssl

# 硅基流动配置
api_key = "sk-yejrmdhdkioqibkiangxahwhzbdxkccajddgyoplwqxyobte"
base_url = "https://api.siliconflow.cn/v1"
# 常见模型列表（按可能性排序）
models = [
    "deepseek-ai/DeepSeek-V3",
    "deepseek-ai/DeepSeek-R1",
    "Qwen/Qwen2.5-7B-Instruct",
    "THUDM/glm-4-9b-chat",
    "gpt-3.5-turbo" #有些中转商会把硅基流动的模型映射为这个名字
]

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

print(f"Testing SiliconFlow API with Key: {api_key[:10]}...")

for model in models:
    print(f"\n--- Testing Model: {model} ---")
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "Hello"}],
        "max_tokens": 10,
        "stream": False
    }
    
    try:
        req = urllib.request.Request(
            f"{base_url}/chat/completions",
            data=json.dumps(payload).encode('utf-8'),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            method="POST"
        )
        
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            print(f"✅ SUCCESS! Status: {resp.status}")
            body = resp.read().decode('utf-8')
            print(f"Response: {body[:100]}...")
            print(f"\n[RECOMMENDATION] Please use Model: {model}")
            break # 找到一个能用的就行
            
    except urllib.error.HTTPError as e:
        print(f"❌ Failed: {e.code} {e.reason}")
        print(f"Error Body: {e.read().decode('utf-8')}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
