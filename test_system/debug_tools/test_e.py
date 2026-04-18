import json
import requests
import sys
API_URL = "http://127.0.0.1:8000/api/v1/analyze"
PROVIDER_NAME = "deepseek"
def analyze_with_debug(input_text, sample_id):
    payload = {"chat_text": input_text, "user_question": "", "provider_name": PROVIDER_NAME, "debug": True}
    resp = requests.post(API_URL, json=payload, timeout=120)
    return resp.json()
cases = [
    {"id": "E2", "text": "A：在吗\nB：在"},
    {"id": "E3", "text": "A：今天干嘛了\nB：上班\nA：哦"},
    {"id": "A1", "text": "A：你好\nB：你好\nA：你是哪个专业的\nB：金融\nA：挺不错的"}
]
for case in cases:
    data = analyze_with_debug(case["text"], case["id"])
    stage = data["result"]["relationship_stage"]
    interest = data["result"]["interest_level"]
    print(f"{case['id']}: stage={stage}, interest={interest}")
