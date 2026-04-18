#!/usr/bin/env python3
"""
Test script to verify rules fix for E-group boundary tightening.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.rules.rules import is_very_weak_s2, is_functional_minimal_interaction, is_judgable, infer_relationship_stage, infer_interest_level

def test_e_group():
    """Test E-group samples (should be '无法判断')"""
    print("=== Testing E-group samples ===")

    # E1-like: very weak, single utterance
    s2_e1 = {
        "initiative": "无法判断",
        "response_length": "无法判断",
        "emotional_tone": "无法判断",
        "topic_depth": "无法判断",
        "interaction_reciprocity": "无法判断",
        "key_signals": []
    }
    s3_e1 = {
        "has_intimacy_signal": False,
        "has_relationship_probe": False,
        "has_positive_reciprocity": False,
        "has_rejection_signal": False,
        "has_push_pull_pattern": False,
        "has_sustained_coldness": False,
        "signal_summary": []
    }

    print("E1-like sample:")
    print(f"  is_very_weak_s2: {is_very_weak_s2(s2_e1)}")
    print(f"  is_functional_minimal_interaction: {is_functional_minimal_interaction(s2_e1, s3_e1)}")
    print(f"  is_judgable: {is_judgable(s2_e1, s3_e1)}")
    stage = infer_relationship_stage(s2_e1, s3_e1)
    interest = infer_interest_level(s2_e1, s3_e1, stage)
    print(f"  relationship_stage: {repr(stage)}")
    print(f"  interest_level: {repr(interest)}")
    print()

    # E2-like: minimal functional interaction
    s2_e2 = {
        "initiative": "无法判断",
        "response_length": "短",
        "emotional_tone": "温",
        "topic_depth": "浅",
        "interaction_reciprocity": "弱承接",
        "key_signals": []
    }
    s3_e2 = s3_e1.copy()

    print("E2-like sample:")
    print(f"  is_very_weak_s2: {is_very_weak_s2(s2_e2)}")
    print(f"  is_functional_minimal_interaction: {is_functional_minimal_interaction(s2_e2, s3_e2)}")
    print(f"  is_judgable: {is_judgable(s2_e2, s3_e2)}")
    stage = infer_relationship_stage(s2_e2, s3_e2)
    interest = infer_interest_level(s2_e2, s3_e2, stage)
    print(f"  relationship_stage: {stage}")
    print(f"  interest_level: {interest}")
    print()

    # E3-like: minimal interaction with some signals but insufficient
    s2_e3 = {
        "initiative": "无法判断",
        "response_length": "短",
        "emotional_tone": "温",
        "topic_depth": "浅",
        "interaction_reciprocity": "弱承接",
        "key_signals": ["回复简短"]
    }
    s3_e3 = s3_e1.copy()

    print("E3-like sample:")
    print(f"  is_very_weak_s2: {is_very_weak_s2(s2_e3)}")
    print(f"  is_functional_minimal_interaction: {is_functional_minimal_interaction(s2_e3, s3_e3)}")
    print(f"  is_judgable: {is_judgable(s2_e3, s3_e3)}")
    stage = infer_relationship_stage(s2_e3, s3_e3)
    interest = infer_interest_level(s2_e3, s3_e3, stage)
    print(f"  relationship_stage: {stage}")
    print(f"  interest_level: {interest}")
    print()

def test_a_group():
    """Test A-group samples (should be '初识期')"""
    print("=== Testing A-group samples ===")

    # A1-like: basic acquaintance
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

    print("A1-like sample:")
    print(f"  is_very_weak_s2: {is_very_weak_s2(s2_a1)}")
    print(f"  is_functional_minimal_interaction: {is_functional_minimal_interaction(s2_a1, s3_a1)}")
    print(f"  is_judgable: {is_judgable(s2_a1, s3_a1)}")
    stage = infer_relationship_stage(s2_a1, s3_a1)
    interest = infer_interest_level(s2_a1, s3_a1, stage)
    print(f"  relationship_stage: {stage}")
    print(f"  interest_level: {interest}")
    print()

    # A2-like: warmer acquaintance
    s2_a2 = {
        "initiative": "双方接近",
        "response_length": "中",
        "emotional_tone": "热",
        "topic_depth": "中",
        "interaction_reciprocity": "正向承接",
        "key_signals": ["表达共情", "提出邀约"]
    }
    s3_a2 = s3_a1.copy()

    print("A2-like sample:")
    print(f"  is_very_weak_s2: {is_very_weak_s2(s2_a2)}")
    print(f"  is_functional_minimal_interaction: {is_functional_minimal_interaction(s2_a2, s3_a2)}")
    print(f"  is_judgable: {is_judgable(s2_a2, s3_a2)}")
    stage = infer_relationship_stage(s2_a2, s3_a2)
    interest = infer_interest_level(s2_a2, s3_a2, stage)
    print(f"  relationship_stage: {stage}")
    print(f"  interest_level: {interest}")
    print()

    # A3-like: compliment boundary
    s2_a3 = {
        "initiative": "一方主动",
        "response_length": "中",
        "emotional_tone": "热",
        "topic_depth": "浅",
        "interaction_reciprocity": "正向承接",
        "key_signals": ["互相夸奖"]
    }
    s3_a3 = s3_a1.copy()

    print("A3-like sample:")
    print(f"  is_very_weak_s2: {is_very_weak_s2(s2_a3)}")
    print(f"  is_functional_minimal_interaction: {is_functional_minimal_interaction(s2_a3, s3_a3)}")
    print(f"  is_judgable: {is_judgable(s2_a3, s3_a3)}")
    stage = infer_relationship_stage(s2_a3, s3_a3)
    interest = infer_interest_level(s2_a3, s3_a3, stage)
    print(f"  relationship_stage: {stage}")
    print(f"  interest_level: {interest}")
    print()

def test_edge_cases():
    """Test edge cases"""
    print("=== Testing edge cases ===")

    # Sample with only key_signals but weak S2
    s2_edge = {
        "initiative": "无法判断",
        "response_length": "短",
        "emotional_tone": "温",
        "topic_depth": "浅",
        "interaction_reciprocity": "弱承接",
        "key_signals": ["回复简短"]
    }
    s3_edge = {
        "has_intimacy_signal": False,
        "has_relationship_probe": False,
        "has_positive_reciprocity": False,
        "has_rejection_signal": False,
        "has_push_pull_pattern": False,
        "has_sustained_coldness": False,
        "signal_summary": []
    }

    print("Edge case: weak S2 with key_signals:")
    print(f"  is_very_weak_s2: {is_very_weak_s2(s2_edge)}")
    print(f"  is_functional_minimal_interaction: {is_functional_minimal_interaction(s2_edge, s3_edge)}")
    print(f"  is_judgable: {is_judgable(s2_edge, s3_edge)}")
    stage = infer_relationship_stage(s2_edge, s3_edge)
    interest = infer_interest_level(s2_edge, s3_edge, stage)
    print(f"  relationship_stage: {stage}")
    print(f"  interest_level: {interest}")
    print()

    # Sample with clear signal but weak overall
    s2_edge2 = {
        "initiative": "一方主动",
        "response_length": "短",
        "emotional_tone": "温",
        "topic_depth": "浅",
        "interaction_reciprocity": "弱承接",
        "key_signals": []
    }

    print("Edge case: clear initiative but otherwise weak:")
    print(f"  is_very_weak_s2: {is_very_weak_s2(s2_edge2)}")
    print(f"  is_functional_minimal_interaction: {is_functional_minimal_interaction(s2_edge2, s3_edge)}")
    print(f"  is_judgable: {is_judgable(s2_edge2, s3_edge)}")
    stage = infer_relationship_stage(s2_edge2, s3_edge)
    interest = infer_interest_level(s2_edge2, s3_edge, stage)
    print(f"  relationship_stage: {stage}")
    print(f"  interest_level: {interest}")
    print()

if __name__ == "__main__":
    test_e_group()
    test_a_group()
    test_edge_cases()