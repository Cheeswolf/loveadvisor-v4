import json
import sys
sys.path.insert(0, '.')

from app.rules import rules

# Load test results
with open('test_system/output/test_results.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

samples = {}
for item in data:
    if item['sample_id'] in ['E2', 'E3', 'C1', 'C3']:
        raw = item.get('raw_output', {})
        if isinstance(raw, dict):
            result = raw.get('result', {})
            debug = result.get('debug')
            if debug and isinstance(debug, dict):
                s2 = debug.get('s2')
                s3 = debug.get('s3')
                if s2 and s3:
                    samples[item['sample_id']] = (s2, s3)

# Test each sample
for sample_id, (s2, s3) in samples.items():
    print(f"\n=== Testing {sample_id} ===")
    print("S2:", json.dumps(s2, ensure_ascii=False, indent=2))
    print("S3:", json.dumps(s3, ensure_ascii=False, indent=2))

    # Call rules
    result = rules.infer_r1(s2, s3)
    print("Result:", json.dumps(result, ensure_ascii=False))

    # Also call with debug
    debug_result = rules.infer_r1_with_debug(s2, s3)
    print("Debug flags:", json.dumps(debug_result.get('r1_debug_flags', {}), ensure_ascii=False))
    print("Stage reason:", debug_result.get('r1_stage_reason'))
    print("Interest reason:", debug_result.get('r1_interest_reason'))