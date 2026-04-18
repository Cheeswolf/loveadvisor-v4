#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sys
sys.path.insert(0, '.')

from app.rules.rules import infer_r1_with_debug

# Load A2 data
with open('test_system/output/a2_a3_debug_output.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

sample = data['A2']
s2 = sample['debug']['r1_input']['s2']
s3 = sample['debug']['r1_input']['s3']

print("S2:", json.dumps(s2, ensure_ascii=False))
print("S3:", json.dumps(s3, ensure_ascii=False))

r1_result = infer_r1_with_debug(s2, s3)
print("\nR1 result:")
print(json.dumps(r1_result, ensure_ascii=False, indent=2))

print("\nInterest level:", r1_result['interest_level'])
print("Interest reason:", r1_result['r1_interest_reason'])

# Check if interest_level is '中' or '低'
print("\nRaw interest_level value:", repr(r1_result['interest_level']))
print("Type:", type(r1_result['interest_level']))