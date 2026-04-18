# test_system/scripts/debug_s2_s3.py
# -*- coding: utf-8 -*-
"""
Debug script for S2/S3 localization migration.
Tests S2 and S3 prompts and parsers with mock and deepseek providers.
"""

import json
import sys
import asyncio
from pathlib import Path
from typing import Dict, Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

# Import prompts and parsers
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

# Additional test samples
TEST_SAMPLES = [
    {
        "name": "basic_conversation",
        "text": SAMPLE_CONVERSATION
    },
    {
        "name": "warm_interaction",
        "text": """A：今天天气真好，想和你一起去公园散步
B：好呀，我也正想出去走走呢。你什么时候有空？
A：下午三点怎么样？我带点零食
B：太好了！我还可以带我的相机，我们拍点照片"""
    },
    {
        "name": "cold_response",
        "text": """A：周末一起看电影吗？
B：再看吧
A：最近新上了部爱情片，评分挺高的
B：嗯
A：你好像不太感兴趣？
B：忙"""
    }
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
    """Test S2/S3 with a specific provider."""
    print(f"\n{'#' * 50}")
    print(f"Testing {provider_name} provider with sample: {sample['name']}")
    print(f"{'#' * 50}")

    # Create provider
    provider = get_provider(provider_name, provider_config)

    # Test S2
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
        if provider_name == "mock":
            # Mock provider returns generic response, not JSON
            # For testing, we'll directly test parser with expected JSON
            mock_s2_response = {
                "initiative": "A更主动",
                "response_length": "短",
                "emotional_tone": "温",
                "topic_depth": "中",
                "interaction_reciprocity": "弱承接",
                "key_signals": ["A多次主动发起话题", "B回应简短"]
            }
            s2_raw = json.dumps(mock_s2_response, ensure_ascii=False)
        else:
            # For deepseek, use actual API call (stub for now)
            # Since deepseek provider is a stub, we'll also use mock data
            mock_s2_response = {
                "initiative": "双方接近",
                "response_length": "中",
                "emotional_tone": "热",
                "topic_depth": "深",
                "interaction_reciprocity": "正向承接",
                "key_signals": ["双方积极互动", "话题涉及情感"]
            }
            s2_raw = json.dumps(mock_s2_response, ensure_ascii=False)

        pretty_print("S2 Raw LLM Response", s2_raw)

        # Parse S2 response
        s2_parsed = parse_s2_response(s2_raw)
        pretty_print("S2 Parsed Result", s2_parsed)

        # Validate S2
        s2_valid = validate_s2_signals(s2_parsed)
        print(f"S2 Validation: {'PASS' if s2_valid else 'FAIL'}")

    except Exception as e:
        print(f"S2 Error: {e}")
        import traceback
        traceback.print_exc()

    # Test S3
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
            mock_s3_response = {
                "has_intimacy_signal": True,
                "has_relationship_probe": False,
                "has_positive_reciprocity": True,
                "has_rejection_signal": False,
                "has_push_pull_pattern": False,
                "has_sustained_coldness": False,
                "signal_summary": ["双方表达亲密意愿", "互动积极热情"]
            }
            s3_raw = json.dumps(mock_s3_response, ensure_ascii=False)

        pretty_print("S3 Raw LLM Response", s3_raw)

        # Parse S3 response
        s3_parsed = parse_s3_response(s3_raw)
        pretty_print("S3 Parsed Result", s3_parsed)

        # Validate S3
        s3_valid = validate_s3_summary(s3_parsed)
        print(f"S3 Validation: {'PASS' if s3_valid else 'FAIL'}")

    except Exception as e:
        print(f"S3 Error: {e}")
        import traceback
        traceback.print_exc()


async def test_parser_edge_cases():
    """Test parser edge cases with various malformed inputs."""
    print(f"\n{'#' * 50}")
    print("Testing Parser Edge Cases")
    print(f"{'#' * 50}")

    # Test cases for S2 parser
    s2_test_cases = [
        {
            "name": "complete_valid_json",
            "input": '{"initiative": "A更主动", "response_length": "短", "emotional_tone": "温", "topic_depth": "浅", "interaction_reciprocity": "弱承接", "key_signals": ["信号1"]}',
            "expected_fields": ["initiative", "response_length", "emotional_tone", "topic_depth", "interaction_reciprocity", "key_signals"]
        },
        {
            "name": "missing_fields",
            "input": '{"initiative": "A更主动", "response_length": "短"}',
            "expected_fields": ["initiative", "response_length", "emotional_tone", "topic_depth", "interaction_reciprocity", "key_signals"]
        },
        {
            "name": "invalid_enum_value",
            "input": '{"initiative": "invalid", "response_length": "短", "emotional_tone": "温", "topic_depth": "浅", "interaction_reciprocity": "弱承接", "key_signals": []}',
            "expected_initiative": "无法判断"
        },
        {
            "name": "key_signals_as_string",
            "input": '{"initiative": "A更主动", "response_length": "短", "emotional_tone": "温", "topic_depth": "浅", "interaction_reciprocity": "弱承接", "key_signals": "单一信号"}',
            "expected_key_signals_type": list
        },
        {
            "name": "json_with_markdown",
            "input": '```json\n{"initiative": "A更主动", "response_length": "短", "emotional_tone": "温", "topic_depth": "浅", "interaction_reciprocity": "弱承接", "key_signals": ["信号1"]}\n```',
            "expected_fields": ["initiative", "response_length", "emotional_tone", "topic_depth", "interaction_reciprocity", "key_signals"]
        },
    ]

    for case in s2_test_cases:
        print(f"\n--- S2 Test Case: {case['name']} ---")
        pretty_print("Input", case['input'])
        try:
            result = parse_s2_response(case['input'])
            pretty_print("Parsed Result", result)
            valid = validate_s2_signals(result)
            print(f"Validation: {'PASS' if valid else 'FAIL'}")

            # Check specific expectations
            if "expected_initiative" in case:
                if result["initiative"] == case["expected_initiative"]:
                    print(f"✓ Initiative correctly fallback to '{case['expected_initiative']}'")
                else:
                    print(f"✗ Initiative is '{result['initiative']}', expected '{case['expected_initiative']}'")

            if "expected_key_signals_type" in case:
                if isinstance(result["key_signals"], case["expected_key_signals_type"]):
                    print("✓ key_signals is correct type")
                else:
                    print(f"✗ key_signals is {type(result['key_signals'])}, expected {case['expected_key_signals_type']}")

        except Exception as e:
            print(f"Error: {e}")

    # Test cases for S3 parser
    s3_test_cases = [
        {
            "name": "complete_valid_json",
            "input": '{"has_intimacy_signal": false, "has_relationship_probe": true, "has_positive_reciprocity": true, "has_rejection_signal": false, "has_push_pull_pattern": false, "has_sustained_coldness": false, "signal_summary": ["摘要1"]}',
            "expected_bool_count": 6
        },
        {
            "name": "boolean_as_string",
            "input": '{"has_intimacy_signal": "true", "has_relationship_probe": "false", "has_positive_reciprocity": "yes", "has_rejection_signal": "no", "has_push_pull_pattern": "1", "has_sustained_coldness": "0", "signal_summary": []}',
            "expected_bool_count": 6
        },
        {
            "name": "missing_fields",
            "input": '{"has_intimacy_signal": false, "signal_summary": []}',
            "expected_bool_count": 6
        },
        {
            "name": "signal_summary_as_string",
            "input": '{"has_intimacy_signal": false, "has_relationship_probe": false, "has_positive_reciprocity": false, "has_rejection_signal": false, "has_push_pull_pattern": false, "has_sustained_coldness": false, "signal_summary": "单一摘要"}',
            "expected_signal_summary_type": list
        },
    ]

    for case in s3_test_cases:
        print(f"\n--- S3 Test Case: {case['name']} ---")
        pretty_print("Input", case['input'])
        try:
            result = parse_s3_response(case['input'])
            pretty_print("Parsed Result", result)
            valid = validate_s3_summary(result)
            print(f"Validation: {'PASS' if valid else 'FAIL'}")

            # Check specific expectations
            if "expected_bool_count" in case:
                bool_fields = [field for field in result if field.startswith("has_")]
                if len(bool_fields) == case["expected_bool_count"]:
                    print(f"✓ Correct number of boolean fields: {len(bool_fields)}")
                else:
                    print(f"✗ Boolean field count: {len(bool_fields)}, expected {case['expected_bool_count']}")

            if "expected_signal_summary_type" in case:
                if isinstance(result["signal_summary"], case["expected_signal_summary_type"]):
                    print("✓ signal_summary is correct type")
                else:
                    print(f"✗ signal_summary is {type(result['signal_summary'])}, expected {case['expected_signal_summary_type']}")

        except Exception as e:
            print(f"Error: {e}")


async def main():
    """Main test function."""
    print("LoveAdvisor V3 - S2/S3 Localization Migration Debug Script")
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

    # Test parser edge cases
    await test_parser_edge_cases()

    print("\n" + "=" * 100)
    print("Debug script completed")
    print("=" * 100)


if __name__ == "__main__":
    asyncio.run(main())