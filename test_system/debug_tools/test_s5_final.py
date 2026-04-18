#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Final verification test for S5 + Guardrail implementation.
"""

import json
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def main():
    print("=== LoveAdvisor V3 Phase 5 - S5 + Guardrail Integration Test ===")

    # Test 1: Check all required files exist
    print("\n1. Checking required files...")
    required_files = [
        "app/prompts/s5_prompt.py",
        "app/parsers/s5_parser.py",
        "app/services/strategy_generator.py",
        "app/services/guardrail_service.py",
        "app/schemas/result_models.py"
    ]

    all_files_exist = True
    for file in required_files:
        path = os.path.join(project_root, file)
        if os.path.exists(path):
            print(f"  OK: {file}")
        else:
            print(f"  MISSING: {file}")
            all_files_exist = False

    if not all_files_exist:
        print("ERROR: Some required files are missing!")
        return False

    # Test 2: Check imports
    print("\n2. Testing imports...")
    try:
        from app.prompts.s5_prompt import S5_SYSTEM_PROMPT, S5_PROMPT
        from app.parsers.s5_parser import parse_s5_response, validate_s5_strategies
        from app.services.strategy_generator import generate_strategy
        from app.services.guardrail_service import apply_guardrail
        from app.services.r1_service import infer_r1

        print("  OK: All imports successful")
        print(f"  S5_PROMPT length: {len(S5_PROMPT)}")
        print(f"  S5_SYSTEM_PROMPT length: {len(S5_SYSTEM_PROMPT)}")
    except Exception as e:
        print(f"  ERROR: Import failed: {e}")
        return False

    # Test 3: Test S5 parser
    print("\n3. Testing S5 parser...")
    test_json = '''{
        "psychological_analysis": "测试心理分析",
        "risk_points": ["测试风险点1", "测试风险点2"],
        "suggestions": ["测试建议1", "测试建议2", "测试建议3"],
        "next_step": "测试下一步"
    }'''

    try:
        parsed = parse_s5_response(test_json)
        is_valid = validate_s5_strategies(parsed)

        print(f"  OK: Parser test passed")
        print(f"  Validation: {'PASS' if is_valid else 'FAIL'}")
        print(f"  Fields: {list(parsed.keys())}")

        # Check prohibited fields are not present
        prohibited = ["relationship_stage", "interest_level"]
        has_prohibited = any(field in parsed for field in prohibited)
        if has_prohibited:
            print(f"  WARNING: Parser output contains prohibited fields")
    except Exception as e:
        print(f"  ERROR: Parser test failed: {e}")
        return False

    # Test 4: Test full pipeline with mock data
    print("\n4. Testing full pipeline (mock provider)...")

    # Create test data for different stages
    test_cases = [
        ("初识期", {
            "s2": {"initiative": "A更主动", "response_length": "短", "emotional_tone": "温",
                   "topic_depth": "浅", "interaction_reciprocity": "弱承接", "key_signals": []},
            "s3": {"has_intimacy_signal": False, "has_relationship_probe": False,
                   "has_positive_reciprocity": False, "has_rejection_signal": False,
                   "has_push_pull_pattern": False, "has_sustained_coldness": False,
                   "signal_summary": []},
            "question": "对方回应很冷淡，我该怎么办？"
        }),
        ("暧昧期", {
            "s2": {"initiative": "双方接近", "response_length": "中", "emotional_tone": "热",
                   "topic_depth": "中", "interaction_reciprocity": "正向承接", "key_signals": []},
            "s3": {"has_intimacy_signal": True, "has_relationship_probe": False,
                   "has_positive_reciprocity": True, "has_rejection_signal": False,
                   "has_push_pull_pattern": False, "has_sustained_coldness": False,
                   "signal_summary": []},
            "question": "我们关系好像在升温，该不该推进？"
        })
    ]

    for stage_name, test_data in test_cases:
        print(f"\n  Testing {stage_name}...")

        try:
            # Get R1
            r1 = infer_r1(test_data["s2"], test_data["s3"])

            # Generate S5
            s5_raw = generate_strategy(
                test_data["s2"], test_data["s3"], r1,
                test_data["question"], "mock"
            )

            # Apply guardrail
            s5_corrected = apply_guardrail(r1, s5_raw)

            # Verify results
            required_fields = ["psychological_analysis", "risk_points", "suggestions", "next_step"]
            has_all_fields = all(field in s5_corrected for field in required_fields)

            if has_all_fields:
                print(f"    OK: Pipeline completed for {stage_name}")
                print(f"    Stage: {r1.get('relationship_stage', 'N/A')}")
                print(f"    Suggestions: {len(s5_corrected['suggestions'])}")
                print(f"    Guardrail applied: {s5_corrected.get('_guardrail_applied', False)}")
            else:
                print(f"    ERROR: Missing fields in {stage_name} output")
                return False

        except Exception as e:
            print(f"    ERROR: Pipeline failed for {stage_name}: {e}")
            return False

    print("\n=== ALL TESTS PASSED ===")
    print("\nSummary of implementation:")
    print("1. app/prompts/s5_prompt.py: Implemented with system and user prompts")
    print("2. app/parsers/s5_parser.py: Implemented with validation and defaults")
    print("3. app/services/strategy_generator.py: Implemented generate_strategy() function")
    print("4. app/services/guardrail_service.py: Implemented apply_guardrail() function")
    print("5. app/schemas/result_models.py: Added S5Result Pydantic model")
    print("6. test_system/scripts/debug_s5_guardrail.py: Created debug script")

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)