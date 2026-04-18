"""
LoveAdvisor V3 - Text Utilities
Phase 1: Engineering Skeleton Initialization

This module provides utilities for text processing, cleaning, and analysis.
It includes functions for language detection, keyword extraction, and text normalization.
"""

import re
import string
from typing import List, Optional, Dict, Any, Tuple
import unicodedata
from collections import Counter
import logging

logger = logging.getLogger(__name__)


def clean_text(
    text: str,
    remove_pii: bool = True,
    normalize_whitespace: bool = True,
    remove_urls: bool = True,
    remove_emojis: bool = False,
    lowercase: bool = False,
    max_length: Optional[int] = None
) -> str:
    """
    Clean and normalize text.

    Args:
        text: Input text to clean.
        remove_pii: Whether to remove personally identifiable information.
        normalize_whitespace: Whether to normalize whitespace.
        remove_urls: Whether to remove URLs.
        remove_emojis: Whether to remove emojis.
        lowercase: Whether to convert to lowercase.
        max_length: Maximum length of output text (truncate if longer).

    Returns:
        Cleaned text.
    """
    if not text or not isinstance(text, str):
        return ""

    cleaned = text

    # Remove URLs
    if remove_urls:
        cleaned = _remove_urls(cleaned)

    # Remove PII (basic patterns)
    if remove_pii:
        cleaned = _remove_pii(cleaned)

    # Remove emojis
    if remove_emojis:
        cleaned = _remove_emojis(cleaned)

    # Normalize whitespace
    if normalize_whitespace:
        cleaned = _normalize_whitespace(cleaned)

    # Convert to lowercase
    if lowercase:
        cleaned = cleaned.lower()

    # Truncate if needed
    if max_length and len(cleaned) > max_length:
        cleaned = cleaned[:max_length].rstrip()

    return cleaned


def truncate_text(
    text: str,
    max_length: int,
    suffix: str = "...",
    preserve_words: bool = True
) -> str:
    """
    Truncate text to maximum length.

    Args:
        text: Text to truncate.
        max_length: Maximum length (including suffix if added).
        suffix: Suffix to add if truncated.
        preserve_words: Whether to avoid cutting words in the middle.

    Returns:
        Truncated text.
    """
    if not text or len(text) <= max_length:
        return text

    if preserve_words:
        # Find the last space before max_length
        truncated = text[:max_length - len(suffix)]
        last_space = truncated.rfind(' ')
        if last_space > 0:
            truncated = truncated[:last_space]
    else:
        truncated = text[:max_length - len(suffix)]

    return truncated + suffix


def detect_language(text: str) -> str:
    """
    Detect language of text (simple heuristic).

    Args:
        text: Text to analyze.

    Returns:
        Language code ('zh' for Chinese, 'en' for English, 'unknown' otherwise).
    """
    if not text:
        return "unknown"

    # Check for Chinese characters
    if re.search(r'[\u4e00-\u9fff]', text):
        return "zh"

    # Check for common English patterns
    # Simple heuristic: if text contains mostly Latin characters and common English words
    latin_ratio = len(re.findall(r'[a-zA-Z]', text)) / max(len(text), 1)
    if latin_ratio > 0.7:
        return "en"

    return "unknown"


def extract_keywords(
    text: str,
    max_keywords: int = 10,
    min_word_length: int = 2,
    stopwords: Optional[List[str]] = None
) -> List[Tuple[str, int]]:
    """
    Extract keywords from text.

    Args:
        text: Text to analyze.
        max_keywords: Maximum number of keywords to return.
        min_word_length: Minimum word length to consider.
        stopwords: List of stopwords to exclude.

    Returns:
        List of (keyword, frequency) tuples sorted by frequency.
    """
    if not text:
        return []

    # Default English stopwords
    if stopwords is None:
        stopwords = [
            "a", "an", "the", "and", "or", "but", "in", "on", "at", "to",
            "for", "of", "with", "by", "is", "are", "was", "were", "be",
            "been", "being", "have", "has", "had", "do", "does", "did",
            "will", "would", "should", "could", "can", "may", "might",
            "must", "i", "you", "he", "she", "it", "we", "they", "me",
            "him", "her", "us", "them", "my", "your", "his", "its",
            "our", "their", "mine", "yours", "hers", "ours", "theirs"
        ]

    # Clean and tokenize text
    cleaned = clean_text(text, lowercase=True, remove_urls=True, remove_emojis=True)
    words = re.findall(r'\b\w+\b', cleaned)

    # Filter words
    filtered_words = []
    for word in words:
        if (len(word) >= min_word_length and
            word not in stopwords and
            not word.isdigit()):
            filtered_words.append(word)

    # Count frequencies
    word_counts = Counter(filtered_words)

    # Get most common keywords
    keywords = word_counts.most_common(max_keywords)

    return keywords


def calculate_text_similarity(
    text1: str,
    text2: str,
    method: str = "jaccard"
) -> float:
    """
    Calculate similarity between two texts.

    Args:
        text1: First text.
        text2: Second text.
        method: Similarity method ('jaccard', 'cosine', or 'levenshtein').

    Returns:
        Similarity score (0.0-1.0).
    """
    if not text1 or not text2:
        return 0.0

    text1 = clean_text(text1, lowercase=True)
    text2 = clean_text(text2, lowercase=True)

    if method == "jaccard":
        return _jaccard_similarity(text1, text2)
    elif method == "cosine":
        return _cosine_similarity(text1, text2)
    elif method == "levenshtein":
        return _levenshtein_similarity(text1, text2)
    else:
        raise ValueError(f"Unknown similarity method: {method}")


def split_into_sentences(text: str) -> List[str]:
    """
    Split text into sentences.

    Args:
        text: Text to split.

    Returns:
        List of sentences.
    """
    if not text:
        return []

    # Simple sentence splitting (works for English and Chinese)
    # For production, consider using NLTK or other NLP libraries
    sentences = re.split(r'[。！？!?\.]+', text)

    # Clean up sentences
    cleaned_sentences = []
    for sentence in sentences:
        sentence = sentence.strip()
        if sentence:
            cleaned_sentences.append(sentence)

    return cleaned_sentences


def extract_emotions(text: str) -> Dict[str, float]:
    """
    Extract emotion scores from text (basic keyword matching).

    Args:
        text: Text to analyze.

    Returns:
        Dictionary mapping emotions to scores (0.0-1.0).
    """
    # Emotion keywords (English and Chinese)
    emotion_keywords = {
        "happy": ["happy", "joy", "glad", "pleased", "delighted", "开心", "高兴", "快乐"],
        "sad": ["sad", "unhappy", "depressed", "sorrow", "grief", "伤心", "难过", "悲伤"],
        "angry": ["angry", "mad", "furious", "outraged", "irritated", "生气", "愤怒", "恼火"],
        "fear": ["fear", "scared", "afraid", "terrified", "anxious", "害怕", "恐惧", "担心"],
        "surprise": ["surprise", "shocked", "amazed", "astonished", "惊讶", "吃惊", "意外"],
        "love": ["love", "affection", "adore", "cherish", "爱", "喜欢", "疼爱"],
        "disgust": ["disgust", "dislike", "hate", "厌恶", "讨厌", "反感"],
    }

    text_lower = text.lower()
    emotion_counts = {emotion: 0 for emotion in emotion_keywords}
    total_keywords = 0

    # Count emotion keywords
    for emotion, keywords in emotion_keywords.items():
        for keyword in keywords:
            if keyword.lower() in text_lower:
                emotion_counts[emotion] += 1
                total_keywords += 1

    # Calculate scores
    emotion_scores = {}
    if total_keywords > 0:
        for emotion, count in emotion_counts.items():
            emotion_scores[emotion] = count / total_keywords
    else:
        for emotion in emotion_keywords:
            emotion_scores[emotion] = 0.0

    return emotion_scores


# Helper functions
def _remove_urls(text: str) -> str:
    """Remove URLs from text."""
    url_pattern = r'https?://\S+|www\.\S+'
    return re.sub(url_pattern, '', text)


def _remove_pii(text: str) -> str:
    """Remove personally identifiable information."""
    # Phone numbers (Chinese and international formats)
    text = re.sub(r'\b\d{3}[-.]?\d{4}[-.]?\d{4}\b', '[PHONE]', text)
    text = re.sub(r'\b\d{4}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', text)

    # Email addresses
    text = re.sub(r'\b[\w\.-]+@[\w\.-]+\.\w+\b', '[EMAIL]', text)

    # Chinese ID numbers (basic pattern)
    text = re.sub(r'\b\d{17}[\dXx]\b', '[ID]', text)

    return text


def _remove_emojis(text: str) -> str:
    """Remove emojis from text."""
    # Emoji pattern
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "]+",
        flags=re.UNICODE
    )
    return emoji_pattern.sub('', text)


def _normalize_whitespace(text: str) -> str:
    """Normalize whitespace in text."""
    # Replace multiple spaces with single space
    text = re.sub(r'\s+', ' ', text)
    # Remove leading/trailing whitespace
    text = text.strip()
    return text


def _jaccard_similarity(text1: str, text2: str) -> float:
    """Calculate Jaccard similarity between texts."""
    set1 = set(text1.split())
    set2 = set(text2.split())

    if not set1 and not set2:
        return 1.0
    elif not set1 or not set2:
        return 0.0

    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))

    return intersection / union


def _cosine_similarity(text1: str, text2: str) -> float:
    """Calculate cosine similarity between texts."""
    words1 = text1.split()
    words2 = text2.split()

    # Create vocabulary
    vocab = set(words1 + words2)
    if not vocab:
        return 0.0

    # Create vectors
    vec1 = [words1.count(word) for word in vocab]
    vec2 = [words2.count(word) for word in vocab]

    # Calculate dot product
    dot_product = sum(a * b for a, b in zip(vec1, vec2))

    # Calculate magnitudes
    mag1 = sum(a * a for a in vec1) ** 0.5
    mag2 = sum(b * b for b in vec2) ** 0.5

    if mag1 == 0 or mag2 == 0:
        return 0.0

    return dot_product / (mag1 * mag2)


def _levenshtein_similarity(text1: str, text2: str) -> float:
    """Calculate Levenshtein similarity between texts."""
    # For production, use a proper Levenshtein distance implementation
    # This is a simplified version
    if text1 == text2:
        return 1.0

    len1, len2 = len(text1), len(text2)
    max_len = max(len1, len2)

    if max_len == 0:
        return 1.0

    # Simple character-based similarity
    common_chars = sum(1 for c1, c2 in zip(text1, text2) if c1 == c2)
    similarity = common_chars / max_len

    return similarity