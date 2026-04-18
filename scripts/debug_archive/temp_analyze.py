import json
import sys

with open('test_system/output/test_results.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for item in data:
    if item['sample_id'] in ['E2', 'E3', 'C1', 'C3']:
        print(f"\n=== {item['sample_id']} ===")
        print(f"Expected: {item['expected_stage']}/{item['expected_interest']}")
        print(f"Actual: {item['actual_stage']}/{item['actual_interest']}")
        print(f"Stage correct: {item['stage_correct']}")
        print(f"R1 correct: {item['r1_correct']}")
        raw = item.get('raw_output', {})
        if isinstance(raw, dict):
            result = raw.get('result', {})
            debug = result.get('debug')
            if debug:
                print(f"Debug info present: {list(debug.keys()) if isinstance(debug, dict) else 'yes'}")
            else:
                print("No debug info")
        print()