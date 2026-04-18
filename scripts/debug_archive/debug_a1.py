import json
import requests
API_URL = "http://127.0.0.1:8000/api/v1/analyze"
payload = {"chat_text": "A：你好\nB：你好\nA：你是哪个专业的\nB：金融\nA：挺不错的", "user_question": "", "provider_name": "deepseek", "debug": True}
resp = requests.post(API_URL, json=payload, timeout=120)
data = resp.json()
print(json.dumps(data, ensure_ascii=False, indent=2))
