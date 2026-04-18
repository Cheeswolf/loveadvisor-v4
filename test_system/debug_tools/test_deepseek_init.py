#!/usr/bin/env python3
"""
Test DeepSeek provider initialization.
"""
import os
import sys
import asyncio
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Temporarily set environment variable for test
os.environ['DEEPSEEK_API_KEY'] = 'test-key-123'
os.environ['LLM_PROVIDER'] = 'deepseek'

from configs import settings
from app.llm.provider_factory import get_provider
from app.llm.base_provider import LLMRequest

async def test():
    print("=== DeepSeek Provider Initialization Test ===")
    print(f"LLM_PROVIDER: {settings.LLM_PROVIDER}")
    print(f"DEEPSEEK_API_KEY length: {len(settings.DEEPSEEK_API_KEY)}")

    try:
        provider = get_provider('deepseek')
        print(f"Provider created: {provider}")
        print(f"Model name: {provider.get_model_name()}")
        print(f"API key present: {bool(provider.api_key)}")
        print(f"Base URL: {provider.base_url}")

        # Test health check (will likely fail due to invalid API key)
        print("\nTesting health check...")
        try:
            health = await provider.health_check()
            print(f"Health check result: {health}")
        except Exception as e:
            print(f"Health check failed (expected): {e}")

        # Test completion (will likely fail)
        print("\nTesting completion (should fail due to invalid API key)...")
        try:
            request = LLMRequest(prompt="Hello", max_tokens=5)
            response = await provider.complete(request)
            print(f"Unexpected success: {response.text[:50]}")
        except Exception as e:
            print(f"Completion failed (expected): {type(e).__name__}: {e}")

        print("\nInitialization test PASSED (provider created successfully)")
        return True
    except Exception as e:
        print(f"Initialization FAILED: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test())