#!/usr/bin/env python3
"""
Simple test for LLM provider layer.
"""
import asyncio
import sys
from app.llm.provider_factory import get_provider
from app.llm.base_provider import LLMRequest


async def test_provider(provider_name: str, config: dict):
    """Test a provider with given name and config."""
    print(f"\n=== Testing {provider_name} provider ===")
    try:
        provider = get_provider(provider_name, config)
        print(f"Created provider: {provider}")
        print(f"Model name: {provider.get_model_name()}")
        print(f"Supports streaming: {provider.supports_streaming()}")
        print(f"Supports JSON mode: {provider.supports_json_mode()}")

        # Test health check
        health = await provider.health_check()
        print(f"Health check: {health}")

        # Test completion
        request = LLMRequest(prompt="Hello, how are you?", temperature=0.5, max_tokens=100)
        print(f"Sending completion request: {request.prompt[:50]}...")
        response = await provider.complete(request)
        print(f"Response text: {response.text[:100]}...")
        print(f"Response model: {response.model}")
        print(f"Response usage: {response.usage}")

        # Test chat completion
        messages = [
            {"role": "system", "content": "You are a helpful relationship advisor."},
            {"role": "user", "content": "My partner and I argue frequently. What should I do?"}
        ]
        print(f"Sending chat completion with {len(messages)} messages")
        chat_response = await provider.chat_complete(messages, temperature=0.7, max_tokens=200)
        print(f"Chat response: {chat_response.text[:100]}...")

        # Test JSON generation
        print("Testing JSON generation...")
        json_result = await provider.generate_json("Analyze this relationship situation.", schema=None)
        print(f"JSON result: {json_result}")

        # Test cost estimation
        cost = provider.estimate_cost(request)
        print(f"Estimated cost: ${cost:.6f}")

        print(f"[OK] {provider_name} provider tests passed!")
        return True
    except Exception as e:
        print(f"[FAIL] {provider_name} provider test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all provider tests."""
    print("Testing LLM Provider Layer")

    # Test configurations
    test_configs = [
        ("mock", {"model": "mock-model-1.0", "response_delay": 0.01}),
        ("deepseek", {"api_key": "test-key", "model": "deepseek-chat"}),
        ("openai", {"api_key": "test-key", "model": "gpt-3.5-turbo"}),
    ]

    results = []
    for provider_name, config in test_configs:
        try:
            success = await test_provider(provider_name, config)
            results.append((provider_name, success))
        except Exception as e:
            print(f"Failed to test {provider_name}: {e}")
            results.append((provider_name, False))

    print("\n=== Test Summary ===")
    all_passed = True
    for provider_name, success in results:
        status = "PASS" if success else "FAIL"
        print(f"{provider_name}: {status}")
        if not success:
            all_passed = False

    if all_passed:
        print("\nAll provider tests passed!")
    else:
        print("\nSome provider tests failed.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())