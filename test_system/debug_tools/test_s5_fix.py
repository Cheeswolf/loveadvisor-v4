#!/usr/bin/env python3
"""
Test script to verify S5 strategy generation works with empty user_question.
"""
import sys
import asyncio
import json

# Add current directory to Python path
sys.path.insert(0, '.')

from app.services.strategy_generator import generate_strategy_async, generate_strategy

# Mock data similar to A1 sample
mock_s2 = {
    "emotional_signals": [
        {"signal_type": "positive", "text": "对方回复表情符号", "confidence": 0.7}
    ],
    "relational_signals": [
        {"signal_type": "engagement", "text": "回应长度中等", "confidence": 0.6}
    ]
}

mock_s3 = {
    "summary": "互动较为积极，但缺乏深度情感表达。",
    "key_points": ["回复及时", "使用表情符号"],
    "overall_tone": "neutral_positive"
}

mock_r1 = {
    "relationship_stage": "暧昧期",
    "interest_level": "中",
    "next_step_action": "light_probe"
}

async def test_async():
    """Test async function with empty user_question"""
    print("=== Testing generate_strategy_async ===")
    print("Case 1: Empty string user_question")
    try:
        result = await generate_strategy_async(mock_s2, mock_s3, mock_r1, "", "mock")
        print("Success! Result keys:", result.keys())
        print("Psychological analysis:", result.get("psychological_analysis", "N/A"))
        print("Suggestions:", result.get("suggestions", []))
        print("Next step:", result.get("next_step", "N/A"))
        print()
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

    print("Case 2: None user_question")
    try:
        result = await generate_strategy_async(mock_s2, mock_s3, mock_r1, None, "mock")
        print("Success! Result keys:", result.keys())
        print()
    except Exception as e:
        print(f"ERROR: {e}")

    print("Case 3: Valid user_question")
    try:
        result = await generate_strategy_async(mock_s2, mock_s3, mock_r1, "我应该怎么回复她？", "mock")
        print("Success! Result keys:", result.keys())
        print("Psychological analysis:", result.get("psychological_analysis", "N/A"))
        print()
    except Exception as e:
        print(f"ERROR: {e}")

    print("Case 4: Whitespace-only user_question")
    try:
        result = await generate_strategy_async(mock_s2, mock_s3, mock_r1, "   ", "mock")
        print("Success! Result keys:", result.keys())
        print()
    except Exception as e:
        print(f"ERROR: {e}")

def test_sync():
    """Test sync wrapper"""
    print("\n=== Testing generate_strategy (sync) ===")
    print("Case: Empty string user_question")
    try:
        result = generate_strategy(mock_s2, mock_s3, mock_r1, "", "mock")
        print("Success! Result keys:", result.keys())
        print("Psychological analysis:", result.get("psychological_analysis", "N/A"))
        print("Suggestions:", result.get("suggestions", []))
        print("Next step:", result.get("next_step", "N/A"))
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Run async tests
    asyncio.run(test_async())
    # Run sync test
    test_sync()
    print("\nAll tests completed.")