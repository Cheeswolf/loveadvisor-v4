import json
import sys
import requests

API_URL = "http://127.0.0.1:8000/api/v1/analyze"

# Test cases from test_cases.json
test_cases = [
    {
        "sample_id": "E2",
        "input_text": "A：在吗\nB：在",
        "expected_stage": "无法判断",
        "expected_interest": "无法判断"
    },
    {
        "sample_id": "E3",
        "input_text": "A：今天干嘛了\nB：上班\nA：哦",
        "expected_stage": "无法判断",
        "expected_interest": "无法判断"
    },
    {
        "sample_id": "C1",
        "input_text": "A：你最近怎么都不找我\nB：忙\nA：之前不是挺主动的吗\nB：那时候不一样\nA：什么意思\nB：没什么意思",
        "expected_stage": "拉扯期",
        "expected_interest": "中"
    },
    {
        "sample_id": "C3",
        "input_text": "A：我感觉我挺在意你的\nB：嗯\nA：你呢\nB：就那样吧",
        "expected_stage": "拉扯期",
        "expected_interest": "低"
    }
]

for case in test_cases:
    print(f"\n=== Testing {case['sample_id']} ===")
    payload = {
        "chat_text": case["input_text"],
        "user_question": "",
        "provider_name": "deepseek",
        "debug": True
    }
    try:
        response = requests.post(API_URL, json=payload, timeout=120)
        if response.status_code == 200:
            data = response.json()
            result = data.get("result", {})
            stage = result.get("relationship_stage", "无法判断")
            interest = result.get("interest_level", "无法判断")
            print(f"Expected: {case['expected_stage']}/{case['expected_interest']}")
            print(f"Actual: {stage}/{interest}")
            print(f"Stage match: {stage == case['expected_stage']}")
            print(f"Interest match: {interest == case['expected_interest']}")
            # Print debug info if available
            debug = result.get("debug")
            if debug:
                print(f"Debug keys: {list(debug.keys()) if isinstance(debug, dict) else 'present'}")
        else:
            print(f"API error: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Request failed: {e}")