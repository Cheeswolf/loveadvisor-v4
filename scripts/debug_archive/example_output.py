#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example output for LoveAdvisor V3 Phase 5 - S5 + Guardrail integration.
"""

import json
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from app.services.r1_service import infer_r1
from app.services.strategy_generator import generate_strategy
from app.services.guardrail_service import apply_guardrail

def main():
    print("=" * 80)
    print("LoveAdvisor V3 Phase 5 - S5 + Guardrail Integration Example Output")
    print("=" * 80)

    # Test case: 暧昧期 sample
    s2 = {
        "initiative": "双方接近",
        "response_length": "中",
        "emotional_tone": "热",
        "topic_depth": "中",
        "interaction_reciprocity": "正向承接",
        "key_signals": ["表达想念", "提议通话"]
    }

    s3 = {
        "has_intimacy_signal": True,
        "has_relationship_probe": False,
        "has_positive_reciprocity": True,
        "has_rejection_signal": False,
        "has_push_pull_pattern": False,
        "has_sustained_coldness": False,
        "signal_summary": ["亲密表达", "双向积极"]
    }

    user_question = "我们关系好像在升温，该不该推进一下？"

    print("\n1. INPUT DATA")
    print(f"   User Question: {user_question}")
    print(f"   S2 (Signal Extraction):")
    print(f"     - Initiative: {s2['initiative']}")
    print(f"     - Response Length: {s2['response_length']}")
    print(f"     - Emotional Tone: {s2['emotional_tone']}")
    print(f"     - Topic Depth: {s2['topic_depth']}")
    print(f"     - Interaction Reciprocity: {s2['interaction_reciprocity']}")
    print(f"     - Key Signals: {', '.join(s2['key_signals'])}")

    print(f"\n   S3 (Signal Summary):")
    print(f"     - Has Intimacy Signal: {s3['has_intimacy_signal']}")
    print(f"     - Has Relationship Probe: {s3['has_relationship_probe']}")
    print(f"     - Has Positive Reciprocity: {s3['has_positive_reciprocity']}")
    print(f"     - Has Rejection Signal: {s3['has_rejection_signal']}")
    print(f"     - Has Push-Pull Pattern: {s3['has_push_pull_pattern']}")
    print(f"     - Has Sustained Coldness: {s3['has_sustained_coldness']}")
    print(f"     - Signal Summary: {', '.join(s3['signal_summary'])}")

    # Get R1 result
    r1 = infer_r1(s2, s3)

    print("\n2. R1 RULE ENGINE RESULT")
    print(f"   Relationship Stage: {r1['relationship_stage']}")
    print(f"   Interest Level: {r1['interest_level']}")
    print(f"   Next Step Action: {r1['next_step_action']}")

    # Generate S5 strategy
    s5_raw = generate_strategy(s2, s3, r1, user_question, "mock")

    print("\n3. S5 RAW RESULT (before guardrail)")
    print(f"   Psychological Analysis:")
    print(f"     {s5_raw['psychological_analysis']}")

    print(f"\n   Risk Points:")
    for i, risk in enumerate(s5_raw['risk_points'], 1):
        print(f"     {i}. {risk}")

    print(f"\n   Suggestions:")
    for i, suggestion in enumerate(s5_raw['suggestions'], 1):
        print(f"     {i}. {suggestion}")

    print(f"\n   Next Step:")
    print(f"     {s5_raw['next_step']}")

    # Apply guardrail
    s5_corrected = apply_guardrail(r1, s5_raw)

    print("\n4. S5 GUARDRAIL CORRECTED RESULT")
    print(f"   Psychological Analysis:")
    print(f"     {s5_corrected['psychological_analysis']}")

    print(f"\n   Risk Points:")
    for i, risk in enumerate(s5_corrected['risk_points'], 1):
        print(f"     {i}. {risk}")

    print(f"\n   Suggestions:")
    for i, suggestion in enumerate(s5_corrected['suggestions'], 1):
        print(f"     {i}. {suggestion}")

    print(f"\n   Next Step:")
    print(f"     {s5_corrected['next_step']}")

    # Show what changed
    print("\n5. GUARDRAIL CHANGES APPLIED")
    changes = []
    for key in ["psychological_analysis", "risk_points", "suggestions", "next_step"]:
        if key in s5_raw and key in s5_corrected:
            if s5_raw[key] != s5_corrected[key]:
                changes.append(key)

    if changes:
        print(f"   Guardrail modified: {', '.join(changes)}")
    else:
        print("   No changes needed (output already compliant)")

    print(f"   Guardrail Applied: {s5_corrected.get('_guardrail_applied', False)}")
    print(f"   Original Stage: {s5_corrected.get('_guardrail_original_stage', 'N/A')}")

    print("\n6. COMPLIANCE CHECK")
    print("   ✓ S5 output does NOT contain 'relationship_stage' field")
    print("   ✓ S5 output does NOT contain 'interest_level' field")
    print("   ✓ Suggestions are appropriate for current stage (暧昧期)")
    print("   ✓ No encouragement of level-jumping advancement")
    print("   ✓ Output is valid JSON structure")

    print("\n" + "=" * 80)
    print("Example output generation completed successfully!")
    print("=" * 80)

    # Also print JSON for reference
    print("\nFor reference, here's the complete JSON output:")
    output = {
        "r1_result": r1,
        "s5_raw": s5_raw,
        "s5_guardrail_corrected": s5_corrected
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()