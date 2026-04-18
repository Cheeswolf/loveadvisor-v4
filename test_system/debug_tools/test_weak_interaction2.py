#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sys
sys.path.insert(0, '.')

from app.rules.rules import _initial_medium_signal, infer_r1_with_debug

# Load the debug data
with open('test_system/output/a2_a3_debug_output.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for sample_id in ['A2', 'A3']:
    sample = data[sample_id]
    r1_input = sample['debug']['r1_input']
    s2 = r1_input['s2']
    s3 = r1_input['s3']

    print(f"\n=== {sample_id} ===")
    print("S2:", json.dumps(s2, ensure_ascii=False, indent=2))
    print("S3:", json.dumps(s3, ensure_ascii=False, indent=2))

    # Test _initial_medium_signal
    result = _initial_medium_signal(s2, s3)
    print(f"_initial_medium_signal result: {result}")

    # Test full infer_r1_with_debug
    r1_result = infer_r1_with_debug(s2, s3)
    print(f"Full R1 result: {json.dumps(r1_result, ensure_ascii=False, indent=2)}")

    # Check weak_interaction and has_positive_reciprocity
    weak_interaction = (s2.get('response_length') == '短' and s2.get('interaction_reciprocity') == '弱承接')
    print(f"weak_interaction: {weak_interaction}")
    print(f"has_positive_reciprocity: {s3.get('has_positive_reciprocity')}")