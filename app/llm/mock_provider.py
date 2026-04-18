"""
LoveAdvisor V3 - Mock LLM Provider
Phase 1: Engineering Skeleton Initialization

This module implements a mock LLM provider for testing and development.
It returns predefined responses without making actual API calls.
"""

import asyncio
import random
from typing import Dict, Any, List, Optional

from app.llm.base_provider import BaseLLMProvider, LLMRequest, LLMResponse


class MockProvider(BaseLLMProvider):
    """
    Mock LLM provider for testing and development.

    This provider simulates LLM responses without network calls.
    It's useful for:
    - Unit testing pipeline components
    - Development without API costs
    - CI/CD pipeline testing
    - Demonstrating system functionality
    """

    def __init__(self, config: Dict[str, Any], **kwargs):
        """
        Initialize mock provider.

        Args:
            config: Provider configuration (ignored for mock).
            **kwargs: Additional initialization parameters.
        """
        self.config = config.copy()
        self.model = config.get("model", "mock-model-1.0")
        self.response_delay = config.get("response_delay", 0.05)  # seconds
        self.error_rate = config.get("error_rate", 0.0)  # 0-1 probability of error
        self.responses = config.get("responses", [])  # Predefined responses

    async def complete(self, request: LLMRequest) -> LLMResponse:
        """
        Mock completion request.

        Args:
            request: LLM request parameters.

        Returns:
            Mock LLM response.
        """
        # Simulate network delay
        if self.response_delay > 0:
            await asyncio.sleep(self.response_delay)

        # Simulate random errors
        if random.random() < self.error_rate:
            raise Exception("Mock provider simulated error")

        # Generate mock response
        response_text = self._generate_mock_response(request)

        return LLMResponse(
            text=response_text,
            model=self.model,
            usage={
                "prompt_tokens": len(request.prompt) // 4,
                "completion_tokens": random.randint(50, 200),
                "total_tokens": len(request.prompt) // 4 + random.randint(50, 200),
            },
            finish_reason=random.choice(["stop", "length", "content_filter"]),
            raw_response={"mock": True, "prompt_preview": request.prompt[:100]},
        )

    async def chat_complete(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> LLMResponse:
        """
        Mock chat completion request.

        Args:
            messages: List of message dictionaries.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens to generate.
            **kwargs: Additional parameters.

        Returns:
            Mock LLM response.
        """
        if self.response_delay > 0:
            await asyncio.sleep(self.response_delay)

        if random.random() < self.error_rate:
            raise Exception("Mock provider simulated error")

        # Extract last user message
        last_user_message = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                last_user_message = msg.get("content", "")
                break

        # Generate response based on message content
        if "help" in last_user_message.lower():
            response_text = "I understand you need help. Here are some suggestions:\n1. Take a deep breath\n2. Communicate openly\n3. Seek professional support if needed."
        elif "love" in last_user_message.lower():
            response_text = "Love is a complex emotion that requires patience, understanding, and mutual respect. Focus on building trust and communication."
        else:
            response_text = f"[Mock Response] I understand you're saying: '{last_user_message[:50]}...' Based on this, I recommend focusing on clear communication and mutual understanding."

        return LLMResponse(
            text=response_text,
            model=self.model,
            usage={
                "prompt_tokens": sum(len(m.get("content", "")) for m in messages) // 4,
                "completion_tokens": len(response_text) // 4,
                "total_tokens": sum(len(m.get("content", "")) for m in messages) // 4 + len(response_text) // 4,
            },
            finish_reason="stop",
            raw_response={"mock": True, "messages_count": len(messages)},
        )

    def get_model_name(self) -> str:
        """Get the model name."""
        return self.model

    def supports_streaming(self) -> bool:
        """Check if streaming is supported."""
        return False

    def supports_json_mode(self) -> bool:
        """Check if native JSON mode is supported."""
        return False

    async def health_check(self) -> bool:
        """Mock health check always returns True."""
        return True

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
        await asyncio.sleep(self.response_delay)
        # Simulate JSON response based on prompt
        response = {
            "analysis": "Mock JSON analysis based on your input.",
            "confidence": random.uniform(0.7, 0.95),
            "recommendations": ["Communicate openly", "Practice active listening", "Set healthy boundaries"],
            "prompt_preview": prompt[:100]
        }
        # If schema provided, simulate validation
        if schema:
            # Mock validation - just log
            pass
        return response

    def estimate_cost(self, request: LLMRequest) -> float:
        """Mock cost estimation always returns 0."""
        return 0.0

    def _generate_mock_response(self, request: LLMRequest) -> str:
        """
        Generate a mock response based on the request.

        Args:
            request: LLM request.

        Returns:
            Mock response text.
        """
        # Use predefined responses if available
        if self.responses:
            return random.choice(self.responses)

        # Generate response based on prompt content
        prompt_lower = request.prompt.lower()

        if any(word in prompt_lower for word in ["sad", "unhappy", "depressed"]):
            return "I sense you're feeling down. Remember that emotions are temporary. Consider talking to someone you trust or engaging in activities that usually bring you joy."

        elif any(word in prompt_lower for word in ["angry", "mad", "frustrated"]):
            return "Anger is a natural emotion, but it's important to express it constructively. Try taking a few deep breaths before responding, and use 'I feel' statements to communicate."

        elif any(word in prompt_lower for word in ["conflict", "fight", "argument"]):
            return "Conflicts are opportunities for growth. Focus on understanding the other person's perspective, and look for common ground. Remember that resolution is more important than being right."

        elif any(word in prompt_lower for word in ["communication", "talk", "speak"]):
            return "Effective communication involves both speaking and listening. Practice active listening by repeating back what you heard, and express your own needs clearly but respectfully."

        else:
            # Generic relationship advice
            templates = [
                "Based on what you've shared, I recommend focusing on building trust through consistent actions and open communication.",
                "It seems like this situation requires patience and understanding. Consider setting aside dedicated time to discuss concerns without distractions.",
                "Relationship challenges are normal. What's important is how you work through them together. Focus on solutions rather than blame.",
                "Remember that every relationship has its ups and downs. What matters most is mutual respect and willingness to grow together.",
            ]
            return random.choice(templates)