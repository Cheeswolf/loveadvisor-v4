#!/usr/bin/env python3
"""
Test script to verify fallback debug observability.
"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.pipeline_orchestrator import run_analysis_async

async def test_fallback_with_debug():
    """Test that fallback result includes debug info when debug=True."""
    print("Testing fallback debug observability...")

    # Simulate an error by using an invalid provider that will cause an exception
    # We'll monkey-patch _run_s2 to raise an exception
    import app.core.pipeline_orchestrator as orchestrator_module
    original_run_s2 = orchestrator_module._run_s2

    def mock_run_s2(*args, **kwargs):
        raise RuntimeError("Simulated S2 failure for testing")

    orchestrator_module._run_s2 = mock_run_s2

    try:
        # Run analysis with debug=True
        result = await run_analysis_async(
            chat_text="Hello, this is a test conversation.",
            user_question="What should I do?",
            provider_name="mock",  # Not used due to mock
            debug=True
        )

        print("Result keys:", list(result.keys()))
        if "debug" in result:
            print("Debug keys:", list(result["debug"].keys()))
            print("\n=== Debug content ===")
            for key, value in result["debug"].items():
                print(f"{key}: {type(value)}")
                if isinstance(value, dict):
                    print(f"  dict keys: {list(value.keys())}")
                elif isinstance(value, list):
                    print(f"  list length: {len(value)}")
                else:
                    print(f"  value: {repr(value)[:100]}")

            # Check required fields
            required = ["raw_chat_text", "cleaned_chat_text", "s2_input_text", "provider_name",
                       "pipeline_error_stage", "pipeline_error_message", "traceback_summary"]
            missing = [r for r in required if r not in result["debug"]]
            if missing:
                print(f"\n⚠️  Missing required debug fields: {missing}")
            else:
                print(f"\n✅ All required debug fields present")

            # Print example of error fields
            print(f"\n=== Example error fields ===")
            print(f"pipeline_error_stage: {result['debug']['pipeline_error_stage']}")
            print(f"pipeline_error_message: {result['debug']['pipeline_error_message'][:100]}")
            print(f"traceback_summary length: {len(result['debug']['traceback_summary'])}")
            print(f"provider_name: {result['debug']['provider_name']}")
        else:
            print("❌ No debug field in result")

        return result

    finally:
        # Restore original function
        orchestrator_module._run_s2 = original_run_s2

if __name__ == "__main__":
    result = asyncio.run(test_fallback_with_debug())
    print("\n=== Final result (excluding debug) ===")
    for key, value in result.items():
        if key != "debug":
            print(f"{key}: {value}")