"""
LoveAdvisor V3 - Preprocessing Prompts
Phase 1: Engineering Skeleton Initialization

This module contains prompts for the preprocessing stage.
These prompts guide LLMs in cleaning and enriching user input.
"""

PREPROCESS_PROMPT = """
You are a helpful assistant that preprocesses user input for relationship analysis.

Your task is to clean and enrich the user's input to prepare it for signal extraction.

User Input: {user_input}

Additional Context: {user_context}

Instructions:
1. **Clean the text**: Remove any personally identifiable information (names, phone numbers, addresses), URLs, and excessive formatting.
2. **Normalize language**: Correct obvious typos, expand abbreviations, and standardize terminology.
3. **Identify key elements**: Highlight mentions of people, emotions, actions, timeframes, and relationship dynamics.
4. **Enrich context**: Infer missing information that would help analysis (e.g., gender, age range, relationship stage if not explicitly stated).
5. **Flag sensitive content**: Note any content that may indicate safety concerns (abuse, self-harm, etc.).

Output Format (JSON):
{{
  "cleaned_text": "The cleaned and normalized text",
  "enriched_context": {{
    "gender_inferred": "male/female/unknown",
    "age_range_inferred": "teen/20s/30s/40s/50s+/unknown",
    "relationship_stage_inferred": "dating/committed/married/separated/unknown",
    "cultural_context": "east_asian/western/other/unknown"
  }},
  "key_elements": {{
    "people_mentioned": ["person1", "person2"],
    "emotions_detected": ["emotion1", "emotion2"],
    "actions_detected": ["action1", "action2"],
    "timeframes": ["timeframe1", "timeframe2"]
  }},
  "sensitivity_flags": ["flag1", "flag2"],
  "language_detected": "zh/en/other"
}}
"""

# Alternative version for different use cases
PREPROCESS_PROMPT_CONCISE = """
Clean and prepare this relationship advice query: {user_input}

Context: {user_context}

Provide cleaned text and basic context enrichment in JSON format.
"""