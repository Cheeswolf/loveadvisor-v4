#!/usr/bin/env python3
"""
Test configuration loading.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from configs import settings

print("=== Configuration Test ===")
print(f"LLM_PROVIDER: {settings.LLM_PROVIDER}")
print(f"DEEPSEEK_API_KEY (length): {len(settings.DEEPSEEK_API_KEY)}")
print(f"DEEPSEEK_API_KEY (value): {'***' if settings.DEEPSEEK_API_KEY else '(empty)'}")
print(f"OPENAI_API_KEY (length): {len(settings.OPENAI_API_KEY)}")
print(f"ANTHROPIC_API_KEY (length): {len(settings.ANTHROPIC_API_KEY)}")
print(f"ENVIRONMENT: {settings.ENVIRONMENT}")
print(f"DEBUG: {settings.DEBUG}")

# Check if dotenv loaded
env_path = os.path.join(os.path.dirname(__file__), '.env')
print(f".env path: {env_path}")
print(f".env exists: {os.path.exists(env_path)}")