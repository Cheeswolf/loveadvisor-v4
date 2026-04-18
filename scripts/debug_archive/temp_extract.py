import json
import sys

with open('test_system/output/test_results.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for item in data:
    if item['sample_id'] in ['E2', 'E3', 'C1', 'C3']:
        print(f"\n=== {item['sample_id']} ===")
        raw = item.get('raw_output', {})
        if isinstance(raw, dict):
            result = raw.get('result', {})
            debug = result.get('debug')
            if debug and isinstance(debug, dict):
                s2 = debug.get('s2')
                s3 = debug.get('s3')
                if s2:
                    print("S2:", json.dumps(s2, ensure_ascii=False, indent=2))
                if s3:
                    print("S3:", json.dumps(s3, ensure_ascii=False, indent=2))
        print()