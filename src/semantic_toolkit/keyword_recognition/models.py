"""Data models for keyword recognition."""

from enum import Enum
from typing import List


class Language(str, Enum):
    """Supported languages for keyword extraction."""

    CHINESE = "chinese"
    ENGLISH = "english"

    def __str__(self) -> str:
        return self.value


class Keyword:
    """Represents a keyword extracted from scientific literature."""

    text: str
    confidence: float
    position: int
    frequency: int
    category: str

    def __init__(
        self,
        text: str,
        confidence: float,
        position: int = 0,
        frequency: int = 1,
        category: str = "general",
    ):
        self.text = text
        self.confidence = confidence
        self.position = position
        self.frequency = frequency
        self.category = category

    def __repr__(self) -> str:
        return (
            f"Keyword(text='{self.text}', confidence={self.confidence:.2f}, "
            f"position={self.position}, frequency={self.frequency}, category='{self.category}')"
        )

    def __eq__(self, other) -> bool:
        if not isinstance(other, Keyword):
            return False
        return self.text == other.text

    def __hash__(self) -> int:
        return hash(self.text)


class KeywordExtractionResult:
    """Result of keyword extraction from literature text."""

    keywords: List[Keyword]
    language: Language
    summary: dict

    def __init__(self, keywords: List[Keyword], language: Language):
        self.keywords = keywords
        self.language = language
        self.summary = self._compute_summary()

    def _compute_summary(self) -> dict:
        """Compute summary statistics from extracted keywords."""
        total = len(self.keywords)
        if total == 0:
            return {
                "total_keywords": 0,
                "average_confidence": 0.0,
                "categories": {},
                "top_keywords": [],
            }

        avg_confidence = sum(kw.confidence for kw in self.keywords) / total

        category_counts = {}
        for kw in self.keywords:
            category_counts[kw.category] = category_counts.get(kw.category, 0) + 1

        # Get top keywords by confidence
        top_keywords = sorted(
            self.keywords, key=lambda x: (x.confidence, x.frequency), reverse=True
        )[:5]

        return {
            "total_keywords": total,
            "average_confidence": avg_confidence,
            "categories": category_counts,
            "top_keywords": [
                {"text": kw.text, "confidence": kw.confidence} for kw in top_keywords
            ],
        }

    def get_keywords_by_category(self, category: str) -> List[Keyword]:
        """Get keywords filtered by category."""
        return [kw for kw in self.keywords if kw.category == category]

    def get_top_keywords(self, n: int = 10) -> List[Keyword]:
        """Get top N keywords by confidence and frequency."""
        return sorted(
            self.keywords, key=lambda x: (x.confidence, x.frequency), reverse=True
        )[:n]

    def __repr__(self) -> str:
        return (
            f"KeywordExtractionResult(language={self.language}, "
            f"total_keywords={self.summary['total_keywords']}, "
            f"average_confidence={self.summary['average_confidence']:.2f})"
        )
