#!/usr/bin/env python3
"""
Test PREPROCESS stage cleaning logic.
"""
import sys
import asyncio
sys.path.insert(0, '.')

from app.services.preprocess_service import PreprocessService
from app.core.runtime_context import RuntimeContext

async def test_clean_chat_text():
    service = PreprocessService()

    test_cases = [
        ("A: 你好\nB: 你好", "A:/B: format with colon"),
        ("A：你好\nB：你好", "A：/B： format with fullwidth colon"),
        ("A: 你好\nB: 你好\nA: 今天天气不错\nB: 是的", "Multiple turns"),
        ("A: hi\nB: hello", "English chat"),
        ("", "Empty input"),
        ("   ", "Whitespace only"),
        ("A: 你好\n\nB: 你好", "Extra newline"),
        ("A: 你好\nB: 你好", "Short dialogue"),
        ("A: 你好\nB: 你好\n", "Trailing newline"),
    ]

    for chat_text, description in test_cases:
        print(f"\n=== Test: {description} ===")
        print(f"Input: {repr(chat_text)}")
        context = RuntimeContext(
            request_id="test",
            user_input=chat_text,
            user_context={}
        )
        result = await service.execute(context)
        cleaned = result.get("cleaned_text")
        cleaned_chat = result.get("cleaned_chat_text")
        print(f"cleaned_text: {repr(cleaned)}")
        print(f"cleaned_chat_text: {repr(cleaned_chat)}")
        # Ensure not empty if original not empty
        if chat_text.strip():
            if not cleaned:
                print("ERROR: cleaned_text is empty!")
            if not cleaned_chat:
                print("ERROR: cleaned_chat_text is empty!")
        else:
            print("Original empty, skip check")

if __name__ == "__main__":
    asyncio.run(test_clean_chat_text())