import requests
import json

payload = {
    "chat_text": "A：你好\nB：你好",
    "user_question": "",
    "provider_name": "deepseek",
    "debug": False
}

response = requests.post("http://127.0.0.1:8000/api/v1/analyze", json=payload, timeout=30)
print(f"Status: {response.status_code}")
print(f"Response: {response.text[:500]}")