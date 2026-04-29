"""Data models for move recognition."""

from enum import Enum
from typing import List


class MoveType(str, Enum):
    """Types of research moves in an abstract."""

    BACKGROUND = "BACKGROUND"
    PURPOSE = "PURPOSE"
    METHODS = "METHODS"
    RESULTS = "RESULTS"
    CONCLUSIONS = "CONCLUSIONS"

    def __str__(self) -> str:
        return self.value


class Sentence:
    """Represents a sentence in an abstract with its move classification."""

    text: str
    position: int
    move_type: MoveType
    confidence: float

    def __init__(
        self,
        text: str,
        position: int,
        move_type: MoveType,
        confidence: float,
    ):
        self.text = text
        self.position = position
        self.move_type = move_type
        self.confidence = confidence

    def __repr__(self) -> str:
        return (
            f"Sentence(text='{self.text[:50]}...', position={self.position}, "
            f"move_type={self.move_type}, confidence={self.confidence:.2f})"
        )


class AbstractAnalysisResult:
    """Result of abstract analysis with sentence classifications and summary."""

    sentences: List[Sentence]
    summary: dict

    def __init__(self, sentences: List[Sentence]):
        self.sentences = sentences
        self.summary = self._compute_summary()

    def _compute_summary(self) -> dict:
        """Compute summary statistics from the sentences."""
        total = len(self.sentences)
        move_counts = {move_type.value: 0 for move_type in MoveType}

        for sentence in self.sentences:
            move_counts[sentence.move_type.value] += 1

        return {
            "total_sentences": total,
            "move_counts": move_counts,
        }

    def __repr__(self) -> str:
        return (
            f"AbstractAnalysisResult(total_sentences={self.summary['total_sentences']}, "
            f"move_counts={self.summary['move_counts']})"
        )
