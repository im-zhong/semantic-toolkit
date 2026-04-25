"""Keyword recognition module for scientific literature analysis."""

from semantic_toolkit.keyword_recognition.chinese import (
    extract_chinese_keywords,
)
from semantic_toolkit.keyword_recognition.english import (
    extract_english_keywords,
)
from semantic_toolkit.keyword_recognition.models import (
    Keyword,
    KeywordExtractionResult,
    Language,
)

__all__ = [
    "extract_chinese_keywords",
    "extract_english_keywords",
    "extract_keywords",
    "Keyword",
    "KeywordExtractionResult",
    "Language",
]


def extract_keywords(
    text: str,
    language: Language = Language.ENGLISH,
    num_keywords: int = 10,
    **kwargs
) -> KeywordExtractionResult:
    """Extract keywords from scientific literature text.

    This is a unified interface that automatically dispatches to the
    appropriate language-specific extraction function.

    Args:
        text: Text to extract keywords from
        language: Language of the text (chinese or english)
        num_keywords: Number of keywords to extract
        **kwargs: Additional arguments passed to language-specific functions

    Returns:
        KeywordExtractionResult containing extracted keywords and summary

    Raises:
        ValueError: If text is empty or language is invalid
        ImportError: If required packages are not installed

    Example:
        >>> # Extract keywords from Chinese text
        >>> result = extract_keywords(
        ...     "这项研究提出了一种新的深度学习算法...",
        ...     language=Language.CHINESE,
        ...     num_keywords=5
        ... )

        >>> # Extract keywords from English text
        >>> result = extract_keywords(
        ...     "This study proposes a novel deep learning algorithm...",
        ...     language=Language.ENGLISH,
        ...     num_keywords=8
        ... )
    """
    if not text or not text.strip():
        raise ValueError("Text cannot be empty")

    if language == Language.CHINESE:
        return extract_chinese_keywords(text, num_keywords=num_keywords, **kwargs)
    elif language == Language.ENGLISH:
        return extract_english_keywords(text, num_keywords=num_keywords, **kwargs)
    else:
        raise ValueError(f"Unsupported language: {language}")
