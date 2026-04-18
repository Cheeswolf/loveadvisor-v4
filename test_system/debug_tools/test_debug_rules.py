#!/usr/bin/env python3
"""
Debug script to check low information density rule.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.rules.rules import infer_r1_with_debug, is_low_information_density

def test_case(name, s2, s3):
    print(f"\n=== {name} ===")
    print(f"S2: {s2}")
    print(f"S3: {s3}")

    # Check is_low_information_density directly
    debug_info = {}
    low_info = is_low_information_density(s2, debug_info)
    print(f"is_low_information_density: {low_info}")
    print(f"debug_info: {debug_info}")

    # Get full R1 debug
    result = infer_r1_with_debug(s2, s3)
    print(f"relationship_stage: {result['relationship_stage']}")
    print(f"interest_level: {result['interest_level']}")
    print(f"r1_debug_flags: {result['r1_debug_flags']}")
    print(f"r1_stage_reason: {result['r1_stage_reason']}")
    print(f"r1_interest_reason: {result['r1_interest_reason']}")

# E2-like
s2_e2 = {
    "initiative": "无法判断",
    "response_length": "短",
    "emotional_tone": "温",
    "topic_depth": "浅",
    "interaction_reciprocity": "弱承接",
    "key_signals": []
}
s3_e2 = {
    "has_intimacy_signal": False,
    "has_relationship_probe": False,
    "has_positive_reciprocity": False,
    "has_rejection_signal": False,
    "has_push_pull_pattern": False,
    "has_sustained_coldness": False,
    "signal_summary": []
}

# E3-like
s2_e3 = {
    "initiative": "无法判断",
    "response_length": "短",
    "emotional_tone": "温",
    "topic_depth": "浅",
    "interaction_reciprocity": "弱承接",
    "key_signals": ["回复简短"]
}
s3_e3 = s3_e2.copy()

# A1-like
s2_a1 = {
    "initiative": "双方接近",
    "response_length": "中",
    "emotional_tone": "温",
    "topic_depth": "浅",
    "interaction_reciprocity": "弱承接",
    "key_signals": ["互相问候", "询问专业"]
}
s3_a1 = {
    "has_intimacy_signal": False,
    "has_relationship_probe": False,
    "has_positive_reciprocity": False,
    "has_rejection_signal": False,
    "has_push_pull_pattern": False,
    "has_sustained_coldness": False,
    "signal_summary": ["基础互动"]
}

# Test with low information density signals
s2_low_info = {
    "initiative": "无法判断",
    "response_length": "短",
    "emotional_tone": "温",
    "topic_depth": "浅",
    "interaction_reciprocity": "弱承接",
    "key_signals": ["B仅作简短确认", "A未继续追问"]
}
s3_low_info = s3_e2.copy()

test_case("E2", s2_e2, s3_e2)
test_case("E3", s2_e3, s3_e3)
test_case("A1", s2_a1, s3_a1)
test_case("Low info signals", s2_low_info, s3_low_info)