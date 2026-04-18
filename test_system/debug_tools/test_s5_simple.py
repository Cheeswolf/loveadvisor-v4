#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple test for S5 + Guardrail pipeline.
"""

import json
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_s5_guardrail():
    """Test the S5 + Guardrail pipeline."""
    print("Testing S5 + Guardrail pipeline...")

    # Import necessary modules
    try:
        from app.services.r1_service import infer_r1
        from app.services.strategy_generator import generate_strategy
        from app.services.guardrail_service import apply_guardrail

        print("All imports successful")
    except Exception as e:
        print(f"Import failed: {e}")
        return False

    # Create mock S2/S3 for 初识期
    s2 = {
        'initiative': 'A更主动',
        'response_length': '短',
        'emotional_tone': '温',
        'topic_depth': '浅',
        'interaction_reciprocity': '弱承接',
        'key_signals': ['A主动邀约', 'B回应简短']
    }
    s3 = {
        'has_intimacy_signal': False,
        'has_relationship_probe': False,
        'has_positive_reciprocity': False,
        'has_rejection_signal': False,
        'has_push_pull_pattern': False,
        'has_sustained_coldness': False,
        'signal_summary': ['基础功能互动']
    }

    print("\n=== Input Data ===")
    print(f"S2: {json.dumps(s2, ensure_ascii=False)}")
    print(f"S3: {json.dumps(s3, ensure_ascii=False)}")

    # Get R1
    try:
        r1 = infer_r1(s2, s3)
        print(f"\n=== R1 Result ===")
        print(f"Relationship Stage: {r1.get('relationship_stage')}")
        print(f"Interest Level: {r1.get('interest_level')}")
        print(f"Next Step Action: {r1.get('next_step_action')}")
    except Exception as e:
        print(f"✗ R1 inference failed: {e}")
        return False

    # Generate S5
    try:
        s5 = generate_strategy(
            s2=s2,
            s3=s3,
            r1=r1,
            user_question='对方好像对我没什么兴趣，我还要继续主动吗？',
            provider_name='mock'
        )
        print(f"\n=== S5 Raw Result ===")
        print(f"Psychological Analysis: {s5.get('psychological_analysis', 'N/A')[:100]}...")
        print(f"Risk Points: {len(s5.get('risk_points', []))}")
        print(f"Suggestions: {len(s5.get('suggestions', []))}")
        print(f"Next Step: {s5.get('next_step', 'N/A')[:100]}...")
    except Exception as e:
        print(f"✗ S5 generation failed: {e}")
        return False

    # Apply guardrail
    try:
        s5_corrected = apply_guardrail(r1, s5)
        print(f"\n=== S5 Guardrail Corrected ===")
        print(f"Psychological Analysis: {s5_corrected.get('psychological_analysis', 'N/A')[:100]}...")
        print(f"Risk Points: {len(s5_corrected.get('risk_points', []))}")
        print(f"Suggestions: {len(s5_corrected.get('suggestions', []))}")
        print(f"Next Step: {s5_corrected.get('next_step', 'N/A')[:100]}...")

        # Check guardrail metadata
        if s5_corrected.get('_guardrail_applied'):
            print(f"Guardrail Applied: Yes")
            print(f"Original Stage: {s5_corrected.get('_guardrail_original_stage')}")
    except Exception as e:
        print(f"✗ Guardrail application failed: {e}")
        return False

    print("\n=== Test Summary ===")
    print(f"Pipeline completed successfully")
    print(f"Relationship Stage: {r1.get('relationship_stage')}")
    print(f"Interest Level: {r1.get('interest_level')}")
    print(f"S5 Suggestions Count: {len(s5_corrected.get('suggestions', []))}")
    print(f"S5 Risk Points Count: {len(s5_corrected.get('risk_points', []))}")

    return True

if __name__ == "__main__":
    success = test_s5_guardrail()
    sys.exit(0 if success else 1)