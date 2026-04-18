# test_system/scripts/debug_r1.py
# -*- coding: utf-8 -*-
"""
Debug script for R1 local rule engine integration.
Tests R1 rule engine with S2/S3 inputs from mock and deepseek providers.
"""

import json
import sys
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

# Import R1 service
from app.services.r1_service import infer_r1, infer_r1_as_model
# Import prompts and parsers for S2/S3
from app.prompts.s2_prompt import S2_SYSTEM_PROMPT, S2_PROMPT
from app.prompts.s3_prompt import S3_SYSTEM_PROMPT, S3_PROMPT
from app.parsers.s2_parser import parse_s2_response, validate_s2_signals
from app.parsers.s3_parser import parse_s3_response, validate_s3_summary
# Import LLM provider factory
from app.llm.provider_factory import get_provider


SAMPLE_CONVERSATION = """A：你最近是不是对我冷了
B：哪有
A：感觉你没以前那么主动了
B：可能忙吧
A：那你会想我吗
B：会啊
"""

# Additional test samples (at least 2-3)
TEST_SAMPLES = [
    {
        "name": "basic_conversation",
        "text": SAMPLE_CONVERSATION,
        "description": "A expresses feeling coldness, B denies but gives short responses."
    },
    {
        "name": "warm_interaction",
        "text": """A：今天天气真好，想和你一起去公园散步
B：好呀，我也正想出去走走呢。你什么时候有空？
A：下午三点怎么样？我带点零食
B：太好了！我还可以带我的相机，我们拍点照片""",
        "description": "Warm reciprocal interaction with positive reciprocity."
    },
    {
        "name": "cold_response",
        "text": """A：周末一起看电影吗？
B：再看吧
A：最近新上了部爱情片，评分挺高的
B：嗯
A：你好像不太感兴趣？
B：忙""",
        "description": "Cold, dismissive responses with low engagement."
    },
    {
        "name": "ambiguous_push_pull",
        "text": """A：我想你了
B：哦
A：你就这反应？
B：那要怎样
A：你是不是不想理我
B：没有啊，你别多想""",
        "description": "Push-pull pattern with mixed signals."
    },
]


def pretty_print(title: str, data):
    """Pretty print data with title."""
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)
    if isinstance(data, (dict, list)):
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print(data)


async def test_provider(provider_name: str, provider_config: Dict[str, Any], sample: Dict[str, Any]):
    """Test S2/S3 with a specific provider, then run R1."""
    print(f"\n{'#' * 50}")
    print(f"Testing {provider_name} provider with sample: {sample['name']}")
    print(f"{'#' * 50}")
    print(f"Description: {sample['description']}")
    print(f"Conversation:\n{sample['text']}")

    # Create provider (for mock/deepseek stub)
    provider = get_provider(provider_name, provider_config)

    s2_result = None
    s3_result = None

    # --- S2 Signal Extraction ---
    print(f"\n--- S2 Signal Extraction ---")
    s2_prompt = S2_PROMPT.replace('{conversation_text}', sample["text"])
    s2_request = {
        "prompt": s2_prompt,
        "system_prompt": S2_SYSTEM_PROMPT,
        "temperature": 0.1,
        "max_tokens": 1000
    }

    try:
        # Simulate LLM response (mock or deepseek stub)
        # Use predefined mock responses for different samples to demonstrate varied R1 outputs
        if provider_name == "mock":
            if sample["name"] == "warm_interaction":
                mock_s2_response = {
                    "initiative": "双方接近",
                    "response_length": "中",
                    "emotional_tone": "热",
                    "topic_depth": "深",
                    "interaction_reciprocity": "正向承接",
                    "key_signals": ["双方积极互动", "话题涉及共同兴趣"]
                }
            elif sample["name"] == "cold_response":
                mock_s2_response = {
                    "initiative": "A更主动",
                    "response_length": "短",
                    "emotional_tone": "冷",
                    "topic_depth": "浅",
                    "interaction_reciprocity": "明显回避",
                    "key_signals": ["A多次邀请", "B回应冷淡"]
                }
            elif sample["name"] == "ambiguous_push_pull":
                mock_s2_response = {
                    "initiative": "A更主动",
                    "response_length": "短",
                    "emotional_tone": "温",
                    "topic_depth": "中",
                    "interaction_reciprocity": "弱承接",
                    "key_signals": ["A表达思念", "B回应含糊"]
                }
            else:  # basic_conversation
                mock_s2_response = {
                    "initiative": "A更主动",
                    "response_length": "短",
                    "emotional_tone": "温",
                    "topic_depth": "中",
                    "interaction_reciprocity": "弱承接",
                    "key_signals": ["A试探关系状态", "B回应简短"]
                }
            s2_raw = json.dumps(mock_s2_response, ensure_ascii=False)
        else:  # deepseek stub (similar to mock but with slight variations)
            if sample["name"] == "warm_interaction":
                mock_s2_response = {
                    "initiative": "双方接近",
                    "response_length": "长",
                    "emotional_tone": "热",
                    "topic_depth": "深",
                    "interaction_reciprocity": "正向承接",
                    "key_signals": ["积极规划共同活动", "情绪高涨"]
                }
            elif sample["name"] == "cold_response":
                mock_s2_response = {
                    "initiative": "A更主动",
                    "response_length": "短",
                    "emotional_tone": "冷",
                    "topic_depth": "浅",
                    "interaction_reciprocity": "明显回避",
                    "key_signals": ["B回避话题", "对话单方面"]
                }
            elif sample["name"] == "ambiguous_push_pull":
                mock_s2_response = {
                    "initiative": "A更主动",
                    "response_length": "中",
                    "emotional_tone": "温",
                    "topic_depth": "中",
                    "interaction_reciprocity": "弱承接",
                    "key_signals": ["矛盾信号", "既有亲近又有距离"]
                }
            else:
                mock_s2_response = {
                    "initiative": "A更主动",
                    "response_length": "短",
                    "emotional_tone": "温",
                    "topic_depth": "中",
                    "interaction_reciprocity": "弱承接",
                    "key_signals": ["A寻求确认", "B给予有限肯定"]
                }
            s2_raw = json.dumps(mock_s2_response, ensure_ascii=False)

        pretty_print("S2 Raw LLM Response", s2_raw)

        # Parse S2 response
        s2_parsed = parse_s2_response(s2_raw)
        pretty_print("S2 Parsed Result", s2_parsed)

        # Validate S2
        s2_valid = validate_s2_signals(s2_parsed)
        print(f"S2 Validation: {'PASS' if s2_valid else 'FAIL'}")

        s2_result = s2_parsed

    except Exception as e:
        print(f"S2 Error: {e}")
        import traceback
        traceback.print_exc()

    # --- S3 Signal Summary ---
    print(f"\n--- S3 Signal Summary ---")
    s3_prompt = S3_PROMPT.replace('{conversation_text}', sample["text"])
    s3_request = {
        "prompt": s3_prompt,
        "system_prompt": S3_SYSTEM_PROMPT,
        "temperature": 0.1,
        "max_tokens": 1000
    }

    try:
        if provider_name == "mock":
            if sample["name"] == "warm_interaction":
                mock_s3_response = {
                    "has_intimacy_signal": True,
                    "has_relationship_probe": False,
                    "has_positive_reciprocity": True,
                    "has_rejection_signal": False,
                    "has_push_pull_pattern": False,
                    "has_sustained_coldness": False,
                    "signal_summary": ["双方表达亲密意愿", "互动积极热情"]
                }
            elif sample["name"] == "cold_response":
                mock_s3_response = {
                    "has_intimacy_signal": False,
                    "has_relationship_probe": False,
                    "has_positive_reciprocity": False,
                    "has_rejection_signal": True,
                    "has_push_pull_pattern": False,
                    "has_sustained_coldness": True,
                    "signal_summary": ["B表现出明显回避", "互动冷淡"]
                }
            elif sample["name"] == "ambiguous_push_pull":
                mock_s3_response = {
                    "has_intimacy_signal": True,
                    "has_relationship_probe": True,
                    "has_positive_reciprocity": False,
                    "has_rejection_signal": True,
                    "has_push_pull_pattern": True,
                    "has_sustained_coldness": False,
                    "signal_summary": ["混合信号: 亲近与距离并存", "矛盾互动模式"]
                }
            else:
                mock_s3_response = {
                    "has_intimacy_signal": False,
                    "has_relationship_probe": True,
                    "has_positive_reciprocity": True,
                    "has_rejection_signal": False,
                    "has_push_pull_pattern": False,
                    "has_sustained_coldness": False,
                    "signal_summary": ["A试探关系状态", "B给予正面但简短回应"]
                }
            s3_raw = json.dumps(mock_s3_response, ensure_ascii=False)
        else:
            if sample["name"] == "warm_interaction":
                mock_s3_response = {
                    "has_intimacy_signal": True,
                    "has_relationship_probe": True,
                    "has_positive_reciprocity": True,
                    "has_rejection_signal": False,
                    "has_push_pull_pattern": False,
                    "has_sustained_coldness": False,
                    "signal_summary": ["明确亲密表达", "双向积极互动"]
                }
            elif sample["name"] == "cold_response":
                mock_s3_response = {
                    "has_intimacy_signal": False,
                    "has_relationship_probe": False,
                    "has_positive_reciprocity": False,
                    "has_rejection_signal": True,
                    "has_push_pull_pattern": False,
                    "has_sustained_coldness": True,
                    "signal_summary": ["持续冷淡", "缺乏互动意愿"]
                }
            elif sample["name"] == "ambiguous_push_pull":
                mock_s3_response = {
                    "has_intimacy_signal": True,
                    "has_relationship_probe": True,
                    "has_positive_reciprocity": False,
                    "has_rejection_signal": True,
                    "has_push_pull_pattern": True,
                    "has_sustained_coldness": False,
                    "signal_summary": ["推进-后退模式明显", "关系状态不稳定"]
                }
            else:
                mock_s3_response = {
                    "has_intimacy_signal": False,
                    "has_relationship_probe": True,
                    "has_positive_reciprocity": True,
                    "has_rejection_signal": False,
                    "has_push_pull_pattern": False,
                    "has_sustained_coldness": False,
                    "signal_summary": ["关系试探存在", "互动基本正向"]
                }
            s3_raw = json.dumps(mock_s3_response, ensure_ascii=False)

        pretty_print("S3 Raw LLM Response", s3_raw)

        # Parse S3 response
        s3_parsed = parse_s3_response(s3_raw)
        pretty_print("S3 Parsed Result", s3_parsed)

        # Validate S3
        s3_valid = validate_s3_summary(s3_parsed)
        print(f"S3 Validation: {'PASS' if s3_valid else 'FAIL'}")

        s3_result = s3_parsed

    except Exception as e:
        print(f"S3 Error: {e}")
        import traceback
        traceback.print_exc()

    # --- R1 Rule Engine ---
    print(f"\n--- R1 Rule Engine (Local Rules) ---")
    if s2_result is None or s3_result is None:
        print("Skipping R1 because S2 or S3 failed.")
        return

    try:
        # Call R1 service with both dictionary and model interfaces
        r1_dict = infer_r1(s2_result, s3_result)
        pretty_print("R1 Result (Dictionary)", r1_dict)

        r1_model = infer_r1_as_model(s2_result, s3_result)
        pretty_print("R1 Result (Pydantic Model)", r1_model.model_dump())

        # Print summary
        print("\n" + "-" * 50)
        print("SUMMARY:")
        print(f"Relationship Stage: {r1_dict['relationship_stage']}")
        print(f"Interest Level: {r1_dict['interest_level']}")
        print(f"Next Step Action: {r1_dict['next_step_action']}")
        print("-" * 50)

    except Exception as e:
        print(f"R1 Error: {e}")
        import traceback
        traceback.print_exc()


async def test_frozen_data():
    """Test R1 with frozen S2/S3 outputs from data files (optional)."""
    print(f"\n{'#' * 50}")
    print("Testing R1 with Frozen Data Files")
    print(f"{'#' * 50}")

    # Try to load frozen data files if they exist
    frozen_s2_path = PROJECT_ROOT / "test_system" / "data" / "frozen_s2_outputs.json"
    frozen_s3_path = PROJECT_ROOT / "test_system" / "data" / "frozen_s3_outputs.json"

    if frozen_s2_path.exists() and frozen_s3_path.exists():
        try:
            with open(frozen_s2_path, 'r', encoding='utf-8') as f:
                frozen_s2 = json.load(f)
            with open(frozen_s3_path, 'r', encoding='utf-8') as f:
                frozen_s3 = json.load(f)

            print(f"Loaded {len(frozen_s2)} frozen S2 outputs and {len(frozen_s3)} frozen S3 outputs.")

            # Test each pair
            for i, (s2_key, s2_data) in enumerate(frozen_s2.items()):
                s3_data = frozen_s3.get(s2_key)
                if s3_data:
                    print(f"\n--- Frozen Pair {i+1}: {s2_key} ---")
                    pretty_print("S2 Data", s2_data)
                    pretty_print("S3 Data", s3_data)

                    r1_dict = infer_r1(s2_data, s3_data)
                    pretty_print("R1 Result", r1_dict)
                else:
                    print(f"No matching S3 data for key: {s2_key}")
        except Exception as e:
            print(f"Error loading frozen data: {e}")
    else:
        print("Frozen data files not found. Skipping frozen data test.")
        print("To create frozen data files, run the script with --save-frozen flag (not implemented).")


async def main():
    """Main test function."""
    print("LoveAdvisor V3 - R1 Local Rule Engine Integration Debug Script")
    print(f"Project Root: {PROJECT_ROOT}")

    # Provider configurations
    provider_configs = {
        "mock": {
            "model": "mock-model-1.0",
            "response_delay": 0.01,
            "error_rate": 0.0
        },
        "deepseek": {
            "model": "deepseek-chat",
            "api_key": "test_key",  # Not used for stub
            "base_url": "https://api.deepseek.com"
        }
    }

    # Test with each sample
    for sample in TEST_SAMPLES:
        pretty_print(f"Sample: {sample['name']}", sample["text"])

        # Test with mock provider
        await test_provider("mock", provider_configs["mock"], sample)

        # Test with deepseek provider (stub)
        await test_provider("deepseek", provider_configs["deepseek"], sample)

        print("\n" + "=" * 100 + "\n")

    # Test with frozen data (optional)
    await test_frozen_data()

    print("\n" + "=" * 100)
    print("R1 debug script completed")
    print("=" * 100)


if __name__ == "__main__":
    asyncio.run(main())