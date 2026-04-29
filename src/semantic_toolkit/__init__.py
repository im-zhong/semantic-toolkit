"""Semantic Toolkit - A semantic computing toolkit for abstract analysis."""

__version__ = "0.1.0"

# Move recognition module
from semantic_toolkit.move_recognition import (
    AbstractAnalysisResult,
    MoveType,
    Sentence,
    analyze_english_abstract,
)

# Keyword recognition module
from semantic_toolkit.keyword_recognition import (
    Keyword,
    KeywordExtractionResult,
    Language,
    extract_chinese_keywords,
    extract_english_keywords,
    extract_keywords,
)

__all__ = [
    # Move recognition
    "analyze_english_abstract",
    "AbstractAnalysisResult",
    "MoveType",
    "Sentence",
    # Keyword recognition
    "extract_chinese_keywords",
    "extract_english_keywords",
    "extract_keywords",
    "Keyword",
    "KeywordExtractionResult",
    "Language",
]
