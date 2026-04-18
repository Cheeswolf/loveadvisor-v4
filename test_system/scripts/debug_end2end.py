#!/usr/bin/env python3
"""
LoveAdvisor V3 - End-to-End Debug Script
Phase 6: API + Frontend Integration

This script provides end-to-end testing of the complete LoveAdvisor V3 pipeline
by making direct requests to the /analyze API endpoint.

Usage:
    python debug_end2end.py [--debug] [--provider mock|deepseek] [--url URL]

Examples:
    python debug_end2end.py
    python debug_end2end.py --debug --provider mock
    python debug_end2end.py --provider deepseek --url http://localhost:8000
"""

import argparse
import json
import requests
import sys
import time
from typing import Dict, Any, Optional


def test_analysis(
    chat_text: str,
    user_question: str,
    provider: str = "mock",
    debug: bool = False,
    api_url: str = "http://localhost:8000"
) -> Optional[Dict[str, Any]]:
    """
    Test the /analyze endpoint with the given parameters.

    Args:
        chat_text: Conversation text to analyze
        user_question: User's question about the relationship
        provider: LLM provider name
        debug: Enable debug mode
        api_url: Base URL of the API

    Returns:
        Response JSON if successful, None otherwise
    """
    print(f"\n🚀 Testing /analyze endpoint")
    print(f"  Provider: {provider}")
    print(f"  Debug mode: {debug}")
    print(f"  API URL: {api_url}")
    print(f"  Question: {user_question[:50]}...")

    payload = {
        "chat_text": chat_text,
        "user_question": user_question,
        "provider_name": provider,
        "debug": debug
    }

    try:
        start_time = time.time()
        response = requests.post(
            f"{api_url}/analyze",
            json=payload,
            timeout=30
        )
        elapsed = time.time() - start_time

        print(f"  Response time: {elapsed:.2f}s")
        print(f"  Status code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("  ✅ Request successful")
            return result
        else:
            print(f"  ❌ Request failed: {response.status_code}")
            print(f"  Response body: {response.text[:200]}...")
            return None

    except requests.exceptions.RequestException as e:
        print(f"  ❌ Request error: {e}")
        return None


def print_result(result: Dict[str, Any], show_debug: bool = False) -> None:
    """Print analysis results in a readable format."""
    if not result:
        print("No result to display")
        return

    # Extract result data
    result_data = result.get("result", {})
    request_id = result.get("request_id", "N/A")
    status = result.get("status", "unknown")

    print(f"\n📊 ANALYSIS RESULTS")
    print(f"  Request ID: {request_id}")
    print(f"  Status: {status}")

    if status != "success":
        error_msg = result.get("error_message", "Unknown error")
        print(f"  Error: {error_msg}")
        return

    # Main metrics
    print(f"\n  📈 关系阶段: {result_data.get('relationship_stage', 'N/A')}")
    print(f"  📈 兴趣水平: {result_data.get('interest_level', 'N/A')}")

    # Psychological analysis
    analysis = result_data.get('psychological_analysis', '')
    print(f"\n  🧠 心理分析:")
    print(f"    {analysis}")

    # Risk points
    risk_points = result_data.get('risk_points', [])
    print(f"\n  ⚠️  风险点:")
    if risk_points:
        for i, risk in enumerate(risk_points, 1):
            print(f"    {i}. {risk}")
    else:
        print("    未识别到明显风险点")

    # Suggestions
    suggestions = result_data.get('suggestions', [])
    print(f"\n  💡 建议:")
    if suggestions:
        for i, suggestion in enumerate(suggestions, 1):
            print(f"    {i}. {suggestion}")
    else:
        print("    无具体建议")

    # Next step
    next_step = result_data.get('next_step', '')
    print(f"\n  🎯 下一步:")
    print(f"    {next_step}")

    # Debug information
    if show_debug and "debug" in result_data:
        debug_info = result_data["debug"]
        print(f"\n  🔍 调试信息:")

        if "s2" in debug_info:
            print(f"\n    S2信号提取:")
            s2 = debug_info["s2"]
            print(f"      主动性: {s2.get('initiative', 'N/A')}")
            print(f"      回应长度: {s2.get('response_length', 'N/A')}")
            print(f"      情感基调: {s2.get('emotional_tone', 'N/A')}")
            print(f"      话题深度: {s2.get('topic_depth', 'N/A')}")
            print(f"      互动承接性: {s2.get('interaction_reciprocity', 'N/A')}")
            print(f"      关键信号: {', '.join(s2.get('key_signals', []))}")

        if "s3" in debug_info:
            print(f"\n    S3信号摘要:")
            s3 = debug_info["s3"]
            print(f"      亲密信号: {s3.get('has_intimacy_signal', False)}")
            print(f"      关系试探: {s3.get('has_relationship_probe', False)}")
            print(f"      正向承接: {s3.get('has_positive_reciprocity', False)}")
            print(f"      拒绝信号: {s3.get('has_rejection_signal', False)}")
            print(f"      推拉模式: {s3.get('has_push_pull_pattern', False)}")
            print(f"      持续冷淡: {s3.get('has_sustained_coldness', False)}")
            print(f"      信号摘要: {', '.join(s3.get('signal_summary', []))}")

        if "r1" in debug_info:
            print(f"\n    R1规则推理:")
            r1 = debug_info["r1"]
            print(f"      relationship_stage: {r1.get('relationship_stage', 'N/A')}")
            print(f"      interest_level: {r1.get('interest_level', 'N/A')}")
            print(f"      next_step_action: {r1.get('next_step_action', 'N/A')}")

        if "s5_raw" in debug_info:
            print(f"\n    S5原始输出:")
            s5_raw = debug_info["s5_raw"]
            print(f"      心理分析长度: {len(s5_raw.get('psychological_analysis', ''))} chars")
            print(f"      风险点数量: {len(s5_raw.get('risk_points', []))}")
            print(f"      建议数量: {len(s5_raw.get('suggestions', []))}")

        if "s5_final" in debug_info:
            print(f"\n    S5最终输出 (经过Guardrail):")
            s5_final = debug_info["s5_final"]
            print(f"      心理分析长度: {len(s5_final.get('psychological_analysis', ''))} chars")
            print(f"      风险点数量: {len(s5_final.get('risk_points', []))}")
            print(f"      建议数量: {len(s5_final.get('suggestions', []))}")

    # Metadata
    metadata = result.get("metadata", {})
    if metadata:
        print(f"\n  📋 元数据:")
        for key, value in metadata.items():
            print(f"    {key}: {value}")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="LoveAdvisor V3 End-to-End Debug Script")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--provider", default="mock", choices=["mock", "deepseek"],
                       help="LLM provider to use")
    parser.add_argument("--url", default="http://localhost:8000",
                       help="API base URL (default: http://localhost:8000)")
    parser.add_argument("--test-case", type=int, choices=[1, 2, 3, 4, 5],
                       help="Use predefined test case (1-5)")

    args = parser.parse_args()

    print("=" * 70)
    print("LoveAdvisor V3 - End-to-End Debug Script")
    print("Phase 6: API + Frontend Integration")
    print("=" * 70)

    # Test cases
    test_cases = {
        1: {
            "name": "初识期示例",
            "chat_text": "A: 你好，我是通过朋友介绍认识你的\nB: 你好，很高兴认识你\nA: 听朋友说你也在互联网行业工作？\nB: 是的，我做产品经理",
            "user_question": "对方对我印象如何？"
        },
        2: {
            "name": "暧昧期示例",
            "chat_text": "A: 昨晚的电影真好看，特别是和你一起看\nB: 我也觉得，和你在一起总是很开心\nA: 那下次我们再看一部？\nB: 好呀，你选片",
            "user_question": "我们的关系有发展可能吗？"
        },
        3: {
            "name": "拉扯期示例",
            "chat_text": "A: 我觉得我们最近有点疏远了\nB: 可能是工作太忙了吧\nA: 但我觉得你回复消息也变慢了\nB: 别想太多，我只是最近压力大",
            "user_question": "他是不是在回避我？"
        },
        4: {
            "name": "冷淡期示例",
            "chat_text": "A: 在吗？\nB: 嗯\nA: 晚上一起吃个饭？\nB: 不了，有事\nA: 那明天呢？\nB: 再看吧",
            "user_question": "这段关系还有希望吗？"
        },
        5: {
            "name": "复杂推拉示例",
            "chat_text": "A: 我想你了\nB: 我也是\nA: 那我们周末见面吧？\nB: 这周末可能不行，要加班\nA: 那下周呢？\nB: 再说吧，最近比较忙\nA: 你是不是不想见我？\nB: 不是的，你别多想",
            "user_question": "对方到底对我是什么感觉？"
        }
    }

    # Select test case
    if args.test_case:
        test_case = test_cases[args.test_case]
        chat_text = test_case["chat_text"]
        user_question = test_case["user_question"]
        print(f"\n📋 Using test case {args.test_case}: {test_case['name']}")
    else:
        # Use default test case
        test_case = test_cases[1]
        chat_text = test_case["chat_text"]
        user_question = test_case["user_question"]
        print(f"\n📋 Using default test case: {test_case['name']}")

    # Run test
    result = test_analysis(
        chat_text=chat_text,
        user_question=user_question,
        provider=args.provider,
        debug=args.debug,
        api_url=args.url
    )

    if result:
        print_result(result, show_debug=args.debug)

        # Save result to file for reference
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"debug_result_{timestamp}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n💾 Result saved to: {filename}")

        # Check for errors
        if result.get("status") != "success":
            print(f"\n❌ Analysis failed: {result.get('error_message', 'Unknown error')}")
            sys.exit(1)
        else:
            print(f"\n✅ Analysis completed successfully!")
    else:
        print(f"\n❌ Test failed - no valid response received")
        sys.exit(1)

    print(f"\n🎉 End-to-end test completed!")


if __name__ == "__main__":
    main()