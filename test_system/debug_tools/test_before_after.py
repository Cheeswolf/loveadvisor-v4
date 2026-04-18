#!/usr/bin/env python3
"""
Compare before/after fix for E2 samples with functional signals.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.rules.rules import is_judgable, infer_relationship_stage, infer_r1_with_debug

def simulate_before_fix(s2, s3):
    """Simulate behavior before fix (no functional signal filtering)."""
    # Manually compute key_signals without filtering
    from app.rules.rules import _safe_list, has_any_advanced_signal, is_very_weak_s2 as original_is_very_weak_s2, is_functional_minimal_interaction as original_is_functional_minimal_interaction

    # For simplicity, we'll just call is_judgable with a monkey-patched filter function
    # But we need to modify the module temporarily. Instead, we'll reimplement key parts.
    # Let's just compute the debug flags manually.

    # Simplified simulation: assume key_signals are not filtered
    # We'll compute is_very_weak_s2 without filtering
    key_signals = _safe_list(s2.get("key_signals"))

    # Check is_very_weak_s2 conditions (simplified)
    initiative = s2.get("initiative")
    response_length = s2.get("response_length")
    emotional_tone = s2.get("emotional_tone")
    topic_depth = s2.get("topic_depth")
    interaction_reciprocity = s2.get("interaction_reciprocity")

    is_very_weak = False
    if len(key_signals) == 0:
        is_very_weak = True
    else:
        unknown_count = sum([
            initiative == "无法判断",
            response_length == "无法判断",
            emotional_tone == "无法判断",
            topic_depth == "无法判断",
            interaction_reciprocity == "无法判断",
        ])
        if unknown_count >= 3 and len(key_signals) <= 1:
            is_very_weak = True
        if (initiative in ["无法判断", ""]
            and response_length in ["短", "无法判断", ""]
            and topic_depth in ["浅", "无法判断", ""]
            and interaction_reciprocity in ["弱承接", "无法判断", ""]
            and emotional_tone in ["温", "无法判断", "", "冷"]
            and len(key_signals) <= 1):
            is_very_weak = True

    # is_functional_minimal_interaction (simplified)
    if has_any_advanced_signal(s3):
        is_minimal = False
    else:
        # Check for any clear signal
        has_any_clear_signal = (
            (initiative not in ["无法判断", "", "双方接近"] and initiative is not None)
            or response_length in ["中", "长"]
            or topic_depth in ["中", "深"]
            or interaction_reciprocity in ["正向承接", "明确回避"]
            or emotional_tone in ["热", "冷"]
        )
        if has_any_clear_signal:
            is_minimal = False
        elif len(key_signals) > 0:
            is_minimal = False
        else:
            unknown_count = sum([
                initiative in ["无法判断", "", None],
                response_length in ["无法判断", "", None],
                topic_depth in ["无法判断", "", None],
                interaction_reciprocity in ["无法判断", "", None],
                emotional_tone in ["无法判断", "", "温", None],
            ])
            is_minimal = unknown_count >= 4

    # is_judgable
    if has_any_advanced_signal(s3):
        is_judgable = True
    elif is_very_weak or is_minimal:
        is_judgable = False
    else:
        # Check for clear signals including key_signals
        has_clear_signal = (
            (initiative not in ["无法判断", "", "双方接近"] and initiative is not None)
            or response_length in ["中", "长"]
            or topic_depth in ["中", "深"]
            or interaction_reciprocity in ["正向承接", "明确回避"]
            or emotional_tone in ["热", "冷"]
            or len(key_signals) > 0
        )
        is_judgable = has_clear_signal

    return {
        "is_very_weak_s2": is_very_weak,
        "is_functional_minimal_interaction": is_minimal,
        "is_judgable": is_judgable,
    }

def main():
    print("=== E2 sample with functional signals only ===")
    s2 = {
        "initiative": "无法判断",
        "response_length": "短",
        "emotional_tone": "温",
        "topic_depth": "浅",
        "interaction_reciprocity": "弱承接",
        "key_signals": ["仅作简短确认", "简短回应"]
    }
    s3 = {
        "has_intimacy_signal": False,
        "has_relationship_probe": False,
        "has_positive_reciprocity": False,
        "has_rejection_signal": False,
        "has_push_pull_pattern": False,
        "has_sustained_coldness": False,
        "signal_summary": []
    }

    print("Sample data:")
    print(f"  S2: {s2}")
    print(f"  S3: {s3}")
    print()

    # After fix (current implementation)
    result_after = infer_r1_with_debug(s2, s3)
    print("AFTER FIX (with functional signal filtering):")
    print(f"  relationship_stage: {result_after['relationship_stage']}")
    print(f"  interest_level: {result_after['interest_level']}")
    print(f"  r1_debug_flags: {result_after['r1_debug_flags']}")
    print()

    # Before fix (simulated)
    flags_before = simulate_before_fix(s2, s3)
    print("BEFORE FIX (without functional signal filtering):")
    print(f"  is_very_weak_s2: {flags_before['is_very_weak_s2']}")
    print(f"  is_functional_minimal_interaction: {flags_before['is_functional_minimal_interaction']}")
    print(f"  is_judgable: {flags_before['is_judgable']}")
    print()

    # Determine relationship stage before fix (simplified)
    if flags_before['is_judgable']:
        stage_before = "初识期 (likely)"
    else:
        stage_before = "无法判断"
    print(f"  Inferred relationship stage before fix: {stage_before}")
    print()

    print("=== Summary ===")
    print("Fix ensures that functional signals (e.g., '仅作简短确认', '简短回应') are filtered out.")
    print("Before fix: key_signals counted as valid signals, potentially making is_judgable = True")
    print("After fix: key_signals filtered to empty list, is_very_weak_s2 = True, is_judgable = False")
    print("Thus E2 samples with only functional signals are correctly classified as '无法判断'.")

if __name__ == "__main__":
    main()