#!/usr/bin/env python3
"""
Test functional signal filtering for E2 samples.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.rules.rules import is_judgable, infer_relationship_stage, infer_interest_level, infer_r1_with_debug

def test_e2_functional_signals():
    """Test E2 samples with functional signals in key_signals."""
    print("=== Testing E2 samples with functional signals ===")

    # E2 sample with functional signals only
    s2_e2_func = {
        "initiative": "无法判断",
        "response_length": "短",
        "emotional_tone": "温",
        "topic_depth": "浅",
        "interaction_reciprocity": "弱承接",
        "key_signals": ["仅作简短确认", "简短回应", "单字回应"]
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

    print("E2 with functional signals only:")
    result = infer_r1_with_debug(s2_e2_func, s3_e2)
    print(f"  relationship_stage: {result['relationship_stage']}")
    print(f"  interest_level: {result['interest_level']}")
    print(f"  is_judgable: {result['r1_debug_flags'].get('is_judgable', 'N/A')}")
    print(f"  r1_debug_flags: {result['r1_debug_flags']}")
    print(f"  Expected: relationship_stage = '无法判断', is_judgable = False")
    print()

    # E2 sample with mixed signals: functional + non-functional
    s2_e2_mixed = {
        "initiative": "无法判断",
        "response_length": "短",
        "emotional_tone": "温",
        "topic_depth": "浅",
        "interaction_reciprocity": "弱承接",
        "key_signals": ["仅作简短确认", "表达关心", "单字回应"]
    }

    print("E2 with mixed signals (functional + non-functional):")
    result = infer_r1_with_debug(s2_e2_mixed, s3_e2)
    print(f"  relationship_stage: {result['relationship_stage']}")
    print(f"  interest_level: {result['interest_level']}")
    print(f"  is_judgable: {result['r1_debug_flags'].get('is_judgable', 'N/A')}")
    print(f"  r1_debug_flags: {result['r1_debug_flags']}")
    print(f"  Expected: relationship_stage = '无法判断', is_judgable = False (if only functional signals remain after filtering)")
    print()

    # A1 sample with non-functional signals (should not be affected)
    s2_a1 = {
        "initiative": "双方接近",
        "response_length": "中",
        "emotional_tone": "温",
        "topic_depth": "浅",
        "interaction_reciprocity": "弱承接",
        "key_signals": ["互相问候", "询问专业"]
    }
    s3_a1 = s3_e2.copy()

    print("A1 with non-functional signals (control test):")
    result = infer_r1_with_debug(s2_a1, s3_a1)
    print(f"  relationship_stage: {result['relationship_stage']}")
    print(f"  interest_level: {result['interest_level']}")
    print(f"  is_judgable: {result['r1_debug_flags'].get('is_judgable', 'N/A')}")
    print(f"  r1_debug_flags: {result['r1_debug_flags']}")
    print(f"  Expected: relationship_stage = '初识期', is_judgable = True")
    print()

    # Edge case: functional signal with other clear signals
    s2_edge = {
        "initiative": "一方主动",
        "response_length": "中",
        "emotional_tone": "热",
        "topic_depth": "中",
        "interaction_reciprocity": "正向承接",
        "key_signals": ["仅作简短确认", "表达喜欢"]
    }

    print("Edge case: clear signals + functional signal:")
    result = infer_r1_with_debug(s2_edge, s3_e2)
    print(f"  relationship_stage: {result['relationship_stage']}")
    print(f"  interest_level: {result['interest_level']}")
    print(f"  is_judgable: {result['r1_debug_flags'].get('is_judgable', 'N/A')}")
    print(f"  r1_debug_flags: {result['r1_debug_flags']}")
    print(f"  Expected: relationship_stage = '初识期' (or other), is_judgable = True")
    print()

if __name__ == "__main__":
    test_e2_functional_signals()