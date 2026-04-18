# test_system/scripts/debug_s5_guardrail.py
# -*- coding: utf-8 -*-
"""
Debug script for S5 + Guardrail integration.
Tests S5 strategy generation and guardrail correction with mock and deepseek providers.

Requirements:
1. Support mock provider and deepseek provider
2. At least 3 built-in chat samples
3. Cover at least: 初识期, 暧昧期/拉扯期, 冷淡期/无法判断
4. Print: R1 result, S5 raw result, Guardrail corrected result
"""

import json
import sys
import asyncio
from pathlib import Path
from typing import Dict, Any, List

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

# Import S5 and guardrail modules
from app.prompts.s5_prompt import S5_SYSTEM_PROMPT, S5_PROMPT
from app.parsers.s5_parser import parse_s5_response, validate_s5_strategies
from app.services.strategy_generator import generate_strategy
from app.services.guardrail_service import apply_guardrail
from app.services.r1_service import infer_r1
from app.schemas.result_models import S5Result

# Import LLM provider factory (for reference, though generate_strategy handles it)
from app.llm.provider_factory import get_provider


# ============================================================================
# Test Samples
# ============================================================================

TEST_SAMPLES = [
    {
        "name": "初识期_sample",
        "conversation": """A：你好，最近在忙什么？
B：还行，工作
A：周末有空吗？想约你吃饭
B：再看吧""",
        "user_question": "对方好像对我没什么兴趣，我还要继续主动吗？",
        "description": "初识期，A主动邀约，B回应冷淡简短"
    },
    {
        "name": "暧昧期_sample",
        "conversation": """A：今天下雨了，突然好想你
B：我也想你呀，你在干嘛呢
A：刚下班，有点累，想听听你的声音
B：那我给你打个电话？""",
        "user_question": "我们关系好像在升温，该不该推进一下？",
        "description": "暧昧期，双方表达想念，有亲密互动"
    },
    {
        "name": "拉扯期_sample",
        "conversation": """A：我们到底是什么关系？
B：你说呢
A：我想和你在一起
B：我觉得我们还是做朋友比较好
A：但你上次还说喜欢我
B：那是上次""",
        "user_question": "他忽冷忽热，到底喜不喜欢我？",
        "description": "拉扯期，混合亲密与拒绝信号，矛盾明显"
    },
    {
        "name": "冷淡期_sample",
        "conversation": """A：在吗？
B：嗯
A：最近怎么都不理我
B：忙
A：我们还能回到以前吗？
B：不知道""",
        "user_question": "他已经完全不主动了，我该放弃吗？",
        "description": "冷淡期，互动稀少，回应简短冷淡"
    },
    {
        "name": "无法判断_sample",
        "conversation": """A：哦
B：嗯
A：好吧
B：行""",
        "user_question": "这到底算什么情况？",
        "description": "信号极弱，无法判断阶段"
    }
]


# ============================================================================
# Helper Functions
# ============================================================================

def pretty_print(title: str, data):
    """Pretty print data with title."""
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)
    if isinstance(data, (dict, list)):
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print(data)


def create_mock_s2_s3_for_sample(sample_name: str) -> tuple[Dict[str, Any], Dict[str, Any]]:
    """Create mock S2 and S3 outputs based on sample name."""
    # These mock data should trigger specific R1 stages
    if "初识期" in sample_name:
        s2 = {
            "initiative": "A更主动",
            "response_length": "短",
            "emotional_tone": "温",
            "topic_depth": "浅",
            "interaction_reciprocity": "弱承接",
            "key_signals": ["A主动邀约", "B回应简短"]
        }
        s3 = {
            "has_intimacy_signal": False,
            "has_relationship_probe": False,
            "has_positive_reciprocity": False,
            "has_rejection_signal": False,
            "has_push_pull_pattern": False,
            "has_sustained_coldness": False,
            "signal_summary": ["基础功能互动"]
        }
    elif "暧昧期" in sample_name:
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
    elif "拉扯期" in sample_name:
        s2 = {
            "initiative": "A更主动",
            "response_length": "中",
            "emotional_tone": "温",
            "topic_depth": "深",
            "interaction_reciprocity": "弱承接",
            "key_signals": ["关系试探", "矛盾回应"]
        }
        s3 = {
            "has_intimacy_signal": True,
            "has_relationship_probe": True,
            "has_positive_reciprocity": False,
            "has_rejection_signal": True,
            "has_push_pull_pattern": True,
            "has_sustained_coldness": False,
            "signal_summary": ["推进后退矛盾", "关系状态模糊"]
        }
    elif "冷淡期" in sample_name:
        s2 = {
            "initiative": "A更主动",
            "response_length": "短",
            "emotional_tone": "冷",
            "topic_depth": "浅",
            "interaction_reciprocity": "明显回避",
            "key_signals": ["A多次发起", "B回避冷淡"]
        }
        s3 = {
            "has_intimacy_signal": False,
            "has_relationship_probe": False,
            "has_positive_reciprocity": False,
            "has_rejection_signal": True,
            "has_push_pull_pattern": False,
            "has_sustained_coldness": True,
            "signal_summary": ["持续冷淡", "缺乏互动意愿"]
        }
    else:  # 无法判断
        s2 = {
            "initiative": "无法判断",
            "response_length": "无法判断",
            "emotional_tone": "无法判断",
            "topic_depth": "无法判断",
            "interaction_reciprocity": "无法判断",
            "key_signals": []
        }
        s3 = {
            "has_intimacy_signal": False,
            "has_relationship_probe": False,
            "has_positive_reciprocity": False,
            "has_rejection_signal": False,
            "has_push_pull_pattern": False,
            "has_sustained_coldness": False,
            "signal_summary": ["信号极弱"]
        }

    return s2, s3


# ============================================================================
# Test Functions
# ============================================================================

async def test_s5_guardrail_pipeline(
    provider_name: str,
    sample: Dict[str, Any],
    s2: Dict[str, Any],
    s3: Dict[str, Any]
):
    """Test full S5 + Guardrail pipeline for a sample."""
    print(f"\n{'#' * 50}")
    print(f"Testing {provider_name} provider with sample: {sample['name']}")
    print(f"{'#' * 50}")
    print(f"Description: {sample['description']}")
    print(f"User Question: {sample['user_question']}")
    print(f"Conversation:\n{sample['conversation']}")

    # Step 1: Get R1 result
    print(f"\n--- Step 1: R1 Rule Inference ---")
    try:
        r1_result = infer_r1(s2, s3)
        pretty_print("R1 Result", r1_result)
    except Exception as e:
        print(f"R1 Error: {e}")
        import traceback
        traceback.print_exc()
        return

    # Step 2: Generate S5 strategy
    print(f"\n--- Step 2: S5 Strategy Generation ({provider_name}) ---")
    try:
        s5_raw = generate_strategy(
            s2=s2,
            s3=s3,
            r1=r1_result,
            user_question=sample["user_question"],
            provider_name=provider_name
        )
        pretty_print("S5 Raw Result", s5_raw)

        # Validate S5 result
        s5_valid = validate_s5_strategies(s5_raw)
        print(f"S5 Validation: {'PASS' if s5_valid else 'FAIL'}")

    except Exception as e:
        print(f"S5 Generation Error: {e}")
        import traceback
        traceback.print_exc()
        return

    # Step 3: Apply guardrail
    print(f"\n--- Step 3: Guardrail Correction ---")
    try:
        s5_corrected = apply_guardrail(r1_result, s5_raw)
        pretty_print("S5 Guardrail Corrected Result", s5_corrected)

        # Check what changed
        changes = []
        for key in ["psychological_analysis", "risk_points", "suggestions", "next_step"]:
            if key in s5_raw and key in s5_corrected:
                if s5_raw[key] != s5_corrected[key]:
                    changes.append(key)

        if changes:
            print(f"Guardrail changed fields: {changes}")
        else:
            print("Guardrail made no changes (output already compliant)")

        # Validate as S5Result model
        try:
            s5_model = S5Result(**s5_corrected)
            print(f"S5 Model Validation: PASS")
        except Exception as e:
            print(f"S5 Model Validation Error: {e}")

    except Exception as e:
        print(f"Guardrail Error: {e}")
        import traceback
        traceback.print_exc()
        return

    # Step 4: Summary
    print(f"\n--- Step 4: Pipeline Summary ---")
    print(f"Relationship Stage: {r1_result.get('relationship_stage', 'N/A')}")
    print(f"Interest Level: {r1_result.get('interest_level', 'N/A')}")
    print(f"Next Step Action: {r1_result.get('next_step_action', 'N/A')}")
    print(f"S5 Suggestions Count: {len(s5_corrected.get('suggestions', []))}")
    print(f"S5 Risk Points Count: {len(s5_corrected.get('risk_points', []))}")
    print(f"Guardrail Applied: {s5_corrected.get('_guardrail_applied', False)}")


async def test_parser_edge_cases():
    """Test S5 parser with edge cases."""
    print(f"\n{'#' * 50}")
    print("Testing S5 Parser Edge Cases")
    print(f"{'#' * 50}")

    test_cases = [
        {
            "name": "complete_valid_json",
            "input": '''{
                "psychological_analysis": "用户处于初识期困惑状态",
                "risk_points": ["对方回应较冷淡", "兴趣水平不明确"],
                "suggestions": ["保持轻度互动", "观察对方回应"],
                "next_step": "继续观察，适度互动"
            }''',
            "expected_fields": 4
        },
        {
            "name": "missing_fields",
            "input": '''{
                "psychological_analysis": "测试分析",
                "next_step": "测试步骤"
            }''',
            "expected_fields": 4
        },
        {
            "name": "with_prohibited_fields",
            "input": '''{
                "psychological_analysis": "分析",
                "risk_points": ["风险"],
                "suggestions": ["建议"],
                "next_step": "步骤",
                "relationship_stage": "暧昧期",
                "interest_level": "中"
            }''',
            "expected_prohibited": 0
        },
        {
            "name": "risk_points_as_string",
            "input": '''{
                "psychological_analysis": "分析",
                "risk_points": "单一风险点",
                "suggestions": ["建议1", "建议2"],
                "next_step": "步骤"
            }''',
            "expected_risk_points_type": list
        },
        {
            "name": "json_with_markdown",
            "input": '''```json
            {
                "psychological_analysis": "分析内容",
                "risk_points": ["风险1"],
                "suggestions": ["建议1"],
                "next_step": "下一步"
            }
            ```''',
            "expected_fields": 4
        },
    ]

    for case in test_cases:
        print(f"\n--- Parser Test Case: {case['name']} ---")
        pretty_print("Input", case['input'])
        try:
            result = parse_s5_response(case['input'])
            pretty_print("Parsed Result", result)
            valid = validate_s5_strategies(result)
            print(f"Validation: {'PASS' if valid else 'FAIL'}")

            # Check expectations
            if "expected_fields" in case:
                if len(result) == case["expected_fields"]:
                    print(f"✓ Correct number of fields: {len(result)}")
                else:
                    print(f"✗ Field count: {len(result)}, expected {case['expected_fields']}")

            if "expected_prohibited" in case:
                prohibited_count = sum(1 for field in ["relationship_stage", "interest_level"] if field in result)
                if prohibited_count == case["expected_prohibited"]:
                    print(f"✓ Correct prohibited field count: {prohibited_count}")
                else:
                    print(f"✗ Prohibited field count: {prohibited_count}, expected {case['expected_prohibited']}")

            if "expected_risk_points_type" in case:
                if isinstance(result["risk_points"], case["expected_risk_points_type"]):
                    print("✓ risk_points is correct type")
                else:
                    print(f"✗ risk_points is {type(result['risk_points'])}, expected {case['expected_risk_points_type']}")

        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()


async def test_guardrail_edge_cases():
    """Test guardrail with edge cases."""
    print(f"\n{'#' * 50}")
    print("Testing Guardrail Edge Cases")
    print(f"{'#' * 50}")

    # Test case 1: Stage-inappropriate suggestions
    print("\n--- Test Case 1: Stage-Inappropriate Suggestions ---")
    r1 = {"relationship_stage": "初识期", "interest_level": "中", "next_step_action": "light_reply"}
    s5 = {
        "psychological_analysis": "分析",
        "risk_points": ["风险"],
        "suggestions": ["可以尝试表白确定关系", "每天主动联系增加好感", "保持适度互动"],
        "next_step": "直接问对方是否喜欢自己"
    }
    pretty_print("R1 Input", r1)
    pretty_print("S5 Input (with inappropriate suggestions)", s5)

    corrected = apply_guardrail(r1, s5)
    pretty_print("Guardrail Corrected", corrected)

    # Check that inappropriate suggestions were filtered
    inappropriate_in_corrected = any(
        "表白" in suggestion or "直接问" in suggestion
        for suggestion in corrected.get("suggestions", [])
    )
    if not inappropriate_in_corrected:
        print("✓ Guardrail successfully filtered inappropriate suggestions")
    else:
        print("✗ Guardrail failed to filter inappropriate suggestions")

    # Test case 2: Contradictory next_step
    print("\n--- Test Case 2: Contradictory Next Step ---")
    r2 = {"relationship_stage": "冷淡期", "interest_level": "低", "next_step_action": "pause_contact"}
    s5_2 = {
        "psychological_analysis": "分析",
        "risk_points": ["风险"],
        "suggestions": ["建议"],
        "next_step": "应该每天主动联系挽回感情"
    }
    pretty_print("R1 Input", r2)
    pretty_print("S5 Input (with contradictory next_step)", s5_2)

    corrected2 = apply_guardrail(r2, s5_2)
    pretty_print("Guardrail Corrected", corrected2)

    if "每天主动联系" not in corrected2.get("next_step", ""):
        print("✓ Guardrail corrected contradictory next_step")
    else:
        print("✗ Guardrail failed to correct contradictory next_step")

    # Test case 3: Unsafe suggestions
    print("\n--- Test Case 3: Unsafe Suggestions ---")
    r3 = {"relationship_stage": "拉扯期", "interest_level": "中", "next_step_action": "step_back"}
    s5_3 = {
        "psychological_analysis": "分析",
        "risk_points": ["风险"],
        "suggestions": ["可以威胁对方如果不同意就在一起", "跟踪了解对方行踪", "保持适度距离"],
        "next_step": "保持距离"
    }
    pretty_print("R1 Input", r3)
    pretty_print("S5 Input (with unsafe suggestions)", s5_3)

    corrected3 = apply_guardrail(r3, s5_3)
    pretty_print("Guardrail Corrected", corrected3)

    unsafe_in_corrected = any(
        "威胁" in suggestion or "跟踪" in suggestion
        for suggestion in corrected3.get("suggestions", [])
    )
    if not unsafe_in_corrected:
        print("✓ Guardrail successfully filtered unsafe suggestions")
    else:
        print("✗ Guardrail failed to filter unsafe suggestions")


# ============================================================================
# Main Function
# ============================================================================

async def main():
    """Main test function."""
    print("LoveAdvisor V3 - S5 + Guardrail Integration Debug Script")
    print(f"Project Root: {PROJECT_ROOT}")
    print(f"Test Samples: {len(TEST_SAMPLES)}")

    # Test each sample with mock provider
    for sample in TEST_SAMPLES:
        pretty_print(f"Sample: {sample['name']}", sample["conversation"])

        # Create mock S2/S3 for this sample
        s2, s3 = create_mock_s2_s3_for_sample(sample["name"])
        pretty_print("Mock S2", s2)
        pretty_print("Mock S3", s3)

        # Test with mock provider
        await test_s5_guardrail_pipeline("mock", sample, s2, s3)

        print("\n" + "=" * 100 + "\n")

    # Test parser edge cases
    await test_parser_edge_cases()

    # Test guardrail edge cases
    await test_guardrail_edge_cases()

    print("\n" + "=" * 100)
    print("S5 + Guardrail debug script completed")
    print("=" * 100)


if __name__ == "__main__":
    asyncio.run(main())