#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, '.')

from app.rules.rules import _initial_medium_signal

# A2 data from a2_a3_debug_output.json
s2_a2 = {
    "initiative": "A更主动",
    "response_length": "短",
    "emotional_tone": "温",
    "topic_depth": "浅",
    "interaction_reciprocity": "弱承接",
    "key_signals": [
        "A主动提出邀约（下次一起去）",
        "B使用语气词（哈哈）"
    ]
}

s3_a2 = {
    "has_intimacy_signal": False,
    "has_relationship_probe": False,
    "has_positive_reciprocity": True,
    "has_rejection_signal": False,
    "has_push_pull_pattern": False,
    "has_sustained_coldness": False,
    "signal_summary": [
        "存在双向积极互动：双方轮流发起话题并积极回应",
        "A主动提出未来共同活动（一起去上课）并获得B的同意"
    ]
}

# A3 data
s2_a3 = {
    "initiative": "A更主动",
    "response_length": "短",
    "emotional_tone": "温",
    "topic_depth": "浅",
    "interaction_reciprocity": "弱承接",
    "key_signals": [
        "A主动给予赞美",
        "B使用'哈哈'缓和气氛并礼貌致谢",
        "B给予简短回赞"
    ]
}

s3_a3 = {
    "has_intimacy_signal": False,
    "has_relationship_probe": False,
    "has_positive_reciprocity": True,
    "has_rejection_signal": False,
    "has_push_pull_pattern": False,
    "has_sustained_coldness": False,
    "signal_summary": [
        "存在明显的双向积极互动：A发起赞美，B感谢并回赞"
    ]
}

print("Testing _initial_medium_signal with A2 data:")
result_a2 = _initial_medium_signal(s2_a2, s3_a2)
print(f"Result: {result_a2}")

print("\nTesting _initial_medium_signal with A3 data:")
result_a3 = _initial_medium_signal(s2_a3, s3_a3)
print(f"Result: {result_a3}")

# Debug the function manually
print("\n--- Manual debug ---")
print("A2:")
print(f"  weak_interaction = (response_length=='短' and interaction_reciprocity=='弱承接') = {'短' == '短'} and {'弱承接' == '弱承接'} = True")
print(f"  has_positive_reciprocity = {s3_a2['has_positive_reciprocity']}")
print(f"  score calculation:")
print(f"    has_relationship_probe: {s3_a2['has_relationship_probe']} -> 0")
print(f"    has_positive_reciprocity: {s3_a2['has_positive_reciprocity']} -> +2")
print(f"    emotional_tone=='热': {s2_a2['emotional_tone'] == '热'} -> 0")
print(f"    topic_depth in ['中','深']: {s2_a2['topic_depth'] in ['中','深']} -> 0")
print(f"    interaction_reciprocity=='正向承接': {s2_a2['interaction_reciprocity'] == '正向承接'} -> 0")
print(f"  Total score = 2")
print(f"  score >= 2: True")
print(f"  Compensation branch: weak_interaction and has_positive_reciprocity = True and True = True")
print(f"  Expected: True")
print(f"  Actual: {result_a2}")