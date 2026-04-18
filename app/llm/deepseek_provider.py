"""
LoveAdvisor V3 - DeepSeek LLM Provider
Phase 1: Engineering Skeleton Initialization

This module implements the DeepSeek LLM provider.
It provides integration with DeepSeek's API for Chinese-language optimization.
"""

import asyncio
import json
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.llm.base_provider import BaseLLMProvider, LLMRequest, LLMResponse, LLMError


class DeepSeekProvider(BaseLLMProvider):
    """
    DeepSeek LLM provider implementation.

    This provider is optimized for Chinese language and offers competitive pricing.
    It supports both completion and chat completion endpoints.
    """

    def __init__(self, config: Dict[str, Any], **kwargs):
        """
        Initialize DeepSeek provider.

        Args:
            config: Provider configuration dictionary.
                   Required keys: api_key, base_url (optional), model (optional).
            **kwargs: Additional initialization parameters.
        """
        self.config = config.copy()
        self.api_key = config.get("api_key")
        self.base_url = config.get("base_url", "https://api.deepseek.com")
        self.model = config.get("model", "deepseek-chat")
        self.timeout = config.get("timeout", 30)

        if not self.api_key:
            raise ValueError("DeepSeek provider requires api_key in config")

    async def complete(self, request: LLMRequest) -> LLMResponse:
        """
        Send completion request to DeepSeek API.

        Args:
            request: LLM request parameters.

        Returns:
            LLM response.

        Raises:
            LLMError: If the request fails.
        """
        # Convert completion request to chat format for DeepSeek API
        messages = []
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
        messages.append({"role": "user", "content": request.prompt})

        return await self._make_chat_request(
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            extra_params=request.extra_params
        )

    async def chat_complete(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> LLMResponse:
        """
        Send chat completion request to DeepSeek API.

        Args:
            messages: List of message dictionaries.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens to generate.
            **kwargs: Additional parameters.

        Returns:
            LLM response.
        """
        return await self._make_chat_request(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            extra_params=kwargs
        )

    def get_model_name(self) -> str:
        """Get the model name."""
        return self.model

    def supports_streaming(self) -> bool:
        """Check if streaming is supported."""
        return True

    def supports_json_mode(self) -> bool:
        """Check if native JSON mode is supported."""
        return True

    async def health_check(self) -> bool:
        """Perform health check."""
        try:
            # Try a minimal request
            test_request = LLMRequest(prompt="ping", max_tokens=5)
            await self.complete(test_request)
            return True
        except Exception:
            return False

    async def _make_chat_request(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        extra_params: Optional[Dict[str, Any]] = None
    ) -> LLMResponse:
        """
        Make actual HTTP request to DeepSeek API.

        Args:
            messages: List of message dictionaries.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens to generate.
            extra_params: Additional parameters.

        Returns:
            LLM response.

        Raises:
            LLMError: If the request fails.
        """
        if not self.api_key:
            raise LLMError("DeepSeek API key not configured")

        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }

        if extra_params:
            payload.update(extra_params)

        try:
            # Use asyncio.to_thread to run blocking requests call in thread pool
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.post(url, headers=headers, json=payload, timeout=self.timeout)
            )
            response.raise_for_status()
            result = response.json()

            # Extract response
            if "choices" not in result or len(result["choices"]) == 0:
                raise LLMError(f"No choices in DeepSeek response: {result}")

            choice = result["choices"][0]
            message = choice.get("message", {})
            response_text = message.get("content", "")

            # Extract usage information
            usage = result.get("usage", {})
            usage_dict = {
                "prompt_tokens": usage.get("prompt_tokens", 0),
                "completion_tokens": usage.get("completion_tokens", 0),
                "total_tokens": usage.get("total_tokens", 0)
            }

            # Extract finish reason
            finish_reason = choice.get("finish_reason", "stop")

            return LLMResponse(
                text=response_text,
                model=self.model,
                usage=usage_dict,
                finish_reason=finish_reason,
                raw_response=result
            )

        except requests.exceptions.RequestException as e:
            error_msg = f"DeepSeek API request failed: {str(e)}"
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    error_msg = f"DeepSeek API error: {error_detail}"
                except:
                    error_msg = f"DeepSeek API error: {e.response.text}"
            raise LLMError(error_msg)
        except json.JSONDecodeError as e:
            raise LLMError(f"Failed to parse DeepSeek API response: {str(e)}")
        except Exception as e:
            raise LLMError(f"Unexpected error in DeepSeek provider: {str(e)}")

    async def generate_json(self, prompt: str, schema: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """
        Generate JSON-structured output from the LLM.

        Args:
            prompt: The prompt text.
            schema: Optional JSON schema.
            **kwargs: Additional parameters.

        Returns:
            Parsed JSON dictionary.

        Raises:
            ValueError: If response cannot be parsed as JSON or violates schema.
        """
        # Add JSON format instruction to prompt
        json_prompt = f"{prompt}\n\nPlease respond with valid JSON only."
        if schema:
            schema_str = json.dumps(schema, ensure_ascii=False, indent=2)
            json_prompt = f"{prompt}\n\nPlease respond with valid JSON that follows this schema:\n{schema_str}\n\nRespond with JSON only."

        # Create request
        request = LLMRequest(
            prompt=json_prompt,
            temperature=kwargs.get("temperature", 0.1),  # Low temperature for structured output
            max_tokens=kwargs.get("max_tokens", 2000),
            extra_params=kwargs
        )

        # Call complete method
        response = await self.complete(request)
        response_text = response.text.strip()

        # Try to extract JSON from response (handle cases where LLM adds extra text)
        try:
            # Try to parse directly
            parsed = json.loads(response_text)
        except json.JSONDecodeError:
            # Try to find JSON object in the response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                try:
                    parsed = json.loads(json_match.group())
                except json.JSONDecodeError:
                    raise ValueError(f"Could not parse JSON from response: {response_text[:200]}")
            else:
                raise ValueError(f"No JSON found in response: {response_text[:200]}")

        # Basic schema validation if provided
        if schema:
            # Simple validation: check if all required fields from schema are present
            # This is a simplified validation - for production use a proper JSON schema validator
            required_fields = schema.get("required", [])
            for field in required_fields:
                if field not in parsed:
                    raise ValueError(f"Response missing required field: {field}")

        return parsed

    def estimate_cost(self, request: LLMRequest) -> float:
        """
        Estimate cost based on DeepSeek pricing.

        DeepSeek pricing (approximate as of 2024):
        - Input: $0.14 per 1M tokens
        - Output: $0.28 per 1M tokens

        Args:
            request: LLM request.

        Returns:
            Estimated cost in USD.
        """
        # Rough token estimation (4 chars per token for Chinese/English mix)
        input_tokens = len(request.prompt) // 4
        # Assume 100 output tokens for estimation
        output_tokens = 100

        input_cost = input_tokens * 0.14 / 1_000_000
        output_cost = output_tokens * 0.28 / 1_000_000

        return input_cost + output_cost