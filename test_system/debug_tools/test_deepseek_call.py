#!/usr/bin/env python3
"""
Test DeepSeek API call via pipeline orchestrator.
"""
import os
import sys
import asyncio
import json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Ensure .env is loaded
from configs import settings
print("Settings loaded:")
print(f"LLM_PROVIDER: {settings.LLM_PROVIDER}")
print(f"DEEPSEEK_API_KEY length: {len(settings.DEEPSEEK_API_KEY)}")

async def test():
    print("\n=== Testing DeepSeek API call ===")
    from app.core.pipeline_orchestrator import run_analysis_async
    try:
        result = await run_analysis_async(
            chat_text="你好，最近我和她聊天，她回复很快，也经常发表情包。",
            user_question="她对我有意思吗？",
            provider_name="deepseek",
            debug=True
        )
        print("Result:")
        print(json.dumps(result, ensure_ascii=False, indent=2))

        # Check if result is fallback
        if result.get("relationship_stage") == "无法判断" and result.get("interest_level") == "无法判断":
            print("\nWARNING: Result appears to be fallback output.")
            if "debug" in result:
                print("Debug info available.")
        else:
            print("\nSUCCESS: Got non-fallback result.")

        return True
    except Exception as e:
        print(f"\nERROR: Pipeline failed: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test())
    sys.exit(0 if success else 1)