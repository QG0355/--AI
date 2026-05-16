# -*- coding: utf-8 -*-
"""
Flask AI Chat Service
启动: python flask_ai_server.py
端口: 5000
"""
from flask import Flask, request, jsonify
import os
import json
import re
import ssl
import urllib.request
import urllib.error
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    content = (data.get('message') or data.get('content') or '').strip()
    
    if not content:
        return jsonify({"error": "问题内容不能为空"}), 400

    api_key = os.environ.get('AI_API_KEY') or os.environ.get('OPENAI_API_KEY')
    base_url = (os.environ.get('AI_BASE_URL') or 'https://api.siliconflow.cn/v1').rstrip('/')
    model = os.environ.get('AI_MODEL') or 'deepseek-ai/DeepSeek-V3'
    
    try:
        timeout = float(os.environ.get('AI_TIMEOUT') or 30)
    except Exception:
        timeout = 30.0

    warning = "重要提示：AI 提供的建议请仅供参考，以实际为准，不能盲目操作。"

    if not api_key:
        return jsonify({
            "error": "API_KEY_NOT_SET",
            "fallback": True,
            "warning": warning
        }), 200

    def mask_pii(text):
        text = re.sub(r'\b1\d{10}\b', '[已脱敏手机号]', text)
        text = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '[已脱敏邮箱]', text)
        text = re.sub(r'\b\d{6,}\b', '[已脱敏数字]', text)
        return text

    outbound = mask_pii(content)
    
    system_prompt = (
        "你是校园报修AI助手。请用中文回答，回答要保守、谨慎、以安全为先。"
        "你只能提供报修流程、信息收集建议与风险提示，不能提供任何带电检修、拆装、测电等操作指导。"
        "遇到宿舍水电、安全风险、冒烟、漏电、跳闸等情况，必须提醒用户停止操作并通过平台提交报修等待处理。"
        "不要编造事实或承诺。"
    )
    
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": outbound},
        ],
        "temperature": 0.2,
    }

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    try:
        req = urllib.request.Request(
            f"{base_url}/chat/completions",
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, context=ctx, timeout=timeout) as resp:
            response_data = json.loads(resp.read().decode("utf-8"))
        
        msg = (((response_data.get("choices") or [{}])[0].get("message") or {}).get("content") or "").strip()
        if msg:
            return jsonify({
                "answer": msg, 
                "warning": warning,
                "ai_connected": True
            })
            
    except urllib.error.HTTPError as e:
        err_body = e.read().decode('utf-8') if e.fp else ''
        print(f"[Flask] HTTPError {e.code}: {err_body}")
        return jsonify({
            "error": f"API_ERROR_{e.code}",
            "ai_connected": False,
            "warning": warning
        }), 200
    except urllib.error.URLError as e:
        print(f"[Flask] URLError: {e.reason}")
        return jsonify({
            "error": "NETWORK_ERROR",
            "ai_connected": False,
            "warning": warning
        }), 200
    except Exception as e:
        print(f"[Flask] Error: {e}")
        return jsonify({
            "error": "UNKNOWN_ERROR",
            "ai_connected": False,
            "warning": warning
        }), 200

    return jsonify({
        "error": "NO_RESPONSE",
        "ai_connected": False,
        "warning": warning
    }), 200

@app.route('/health', methods=['GET'])
def health():
    api_key = os.environ.get('AI_API_KEY') or os.environ.get('OPENAI_API_KEY')
    return jsonify({
        "status": "running",
        "ai_configured": bool(api_key),
        "ai_key_preview": api_key[:10] + "..." if api_key else None,
        "base_url": os.environ.get('AI_BASE_URL') or 'https://api.siliconflow.cn/v1',
        "model": os.environ.get('AI_MODEL') or 'deepseek-ai/DeepSeek-V3'
    })

if __name__ == '__main__':
    print("=" * 60)
    print("  Flask AI Service - 校园报修AI助手")
    print("=" * 60)
    
    api_key = os.environ.get('AI_API_KEY') or os.environ.get('OPENAI_API_KEY')
    if api_key:
        print(f"  [OK] API Key: {api_key[:15]}...")
    else:
        print("  [!] AI_API_KEY 未配置，请检查 .env 文件")
    
    print("  [OK] Server: http://localhost:5000")
    print("  [OK] Health: http://localhost:5000/health")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=False)
