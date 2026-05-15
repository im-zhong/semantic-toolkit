"""English abstract move recognition implementation."""

import os
import re
from typing import List

from dotenv import load_dotenv

from semantic_toolkit.move_recognition.models import (
    AbstractAnalysisResult,
    MoveType,
    Sentence,
)

load_dotenv()


def split_into_sentences(text: str) -> List[str]:
    """Split abstract text into sentences.

    Args:
        text: Abstract text to split

    Returns:
        List of sentences
    """
    if not text or not text.strip():
        return []

    # Remove extra whitespace and split by sentence boundaries
    text = text.strip()
    # Simple sentence splitting - split by period, question mark, or exclamation
    # followed by space or end of string
    sentences = re.split(r"(?<=[.!?])\s+", text)

    # Filter out empty strings
    sentences = [s.strip() for s in sentences if s.strip()]

    return sentences


def _build_classification_prompt(sentence: str) -> str:
    """Build prompt for LLM move classification.

    Args:
        sentence: Sentence to classify

    Returns:
        Prompt string for LLM
    """
    move_descriptions = """
BACKGROUND: Describes the context, problem, or gap in knowledge that motivates the research.
PURPOSE: States the objectives, goals, or hypotheses of the study.
METHODS: Describes the research methodology, procedures, or experimental design.
RESULTS: Presents the main findings, data, or outcomes of the study.
CONCLUSIONS: Discusses the implications, interpretations, or recommendations based on results.
"""

    examples = """
Examples:
1. "This study addresses the growing need for efficient data processing in healthcare systems."
   Classification: BACKGROUND

2. "We aim to develop a novel algorithm for large-scale data analysis that improves accuracy."
   Classification: PURPOSE

3. "The proposed method combines deep learning with traditional statistical approaches."
   Classification: METHODS

4. "Results show a 40% improvement in processing speed compared to existing methods."
   Classification: RESULTS

5. "These findings suggest significant potential for real-world applications in clinical settings."
   Classification: CONCLUSIONS
"""

    prompt = f"""Classify the following research sentence into one of five move types.

{move_descriptions}

{examples}

Sentence to classify:
"{sentence}"

Provide your answer in the following JSON format:
{{"move_type": "BACKGROUND|PURPOSE|METHODS|RESULTS|CONCLUSIONS", "confidence": <float between 0 and 1>}}

Respond only with the JSON object, no additional text."""

    return prompt


def _parse_llm_response(response_text: str) -> tuple[MoveType, float]:
    """Parse LLM response to extract move type and confidence.

    Args:
        response_text: Raw LLM response

    Returns:
        Tuple of (MoveType, confidence)
    """
    # Try to extract JSON from response
    import json

    try:
        # Look for JSON pattern in the response
        json_match = re.search(r"\{[^}]*\}", response_text)
        if json_match:
            result = json.loads(json_match.group())
            move_type = MoveType(result["move_type"].upper())
            confidence = float(result.get("confidence", 0.8))
            return move_type, confidence
    except (json.JSONDecodeError, KeyError, ValueError):
        pass

    # Fallback: try to find move type in response
    for move_type in MoveType:
        if move_type.value in response_text:
            return move_type, 0.7

    # Default fallback
    return MoveType.BACKGROUND, 0.5


def classify_sentence_move(sentence: str, llm_client) -> tuple[MoveType, float]:
    """Classify a sentence into a move type using LLM.

    Args:
        sentence: Sentence to classify
        llm_client: LLM client instance

    Returns:
        Tuple of (MoveType, confidence)
    """
    prompt = _build_classification_prompt(sentence)

    try:
        response = llm_client.generate(prompt)
        move_type, confidence = _parse_llm_response(response)
        return move_type, confidence
    except Exception as e:
        print(f"Error classifying sentence: {e}")
        return MoveType.BACKGROUND, 0.0


def _get_llm_client():
    """Get or create LLM client.

    Returns:
        LLM client instance
    """
    try:
        from zai import ZaiClient

        api_key = os.getenv("ZHIPU_API_KEY")
        model = os.getenv("ZHIPU_MODEL", "glm-4")

        if not api_key:
            raise ValueError(
                "ZHIPU_API_KEY environment variable is not set. "
                "Please set it in your .env file or environment."
            )

        client = ZaiClient(api_key=api_key)
        return _LLMClientWrapper(client, model)
    except ImportError:
        raise ImportError(
            "zai-sdk is not installed. Please install it with: "
            "uv add zai-sdk"
        )


class _LLMClientWrapper:
    """Wrapper for ZaiClient to provide a simple generate interface."""

    def __init__(self, client, model):
        self.client = client
        self.model = model

    def generate(self, prompt: str) -> str:
        """Generate a response from the LLM.

        Args:
            prompt: The prompt to send to the LLM

        Returns:
            The generated response text
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content


def analyze_english_abstract(text: str) -> AbstractAnalysisResult:
    """Analyze an English abstract and classify each sentence into move types.

    Args:
        text: Abstract text to analyze

    Returns:
        AbstractAnalysisResult containing sentence classifications and summary

    Raises:
        ValueError: If text is empty or whitespace only
        ImportError: If zai-sdk is not installed
    """
    if not text or not text.strip():
        raise ValueError("Abstract text cannot be empty")

    sentences = split_into_sentences(text)

    if not sentences:
        raise ValueError("Could not extract sentences from the provided text")

    llm_client = _get_llm_client()

    classified_sentences = []
    for idx, sentence in enumerate(sentences):
        print(f"Classifying sentence {idx + 1}/{len(sentences)}...")
        move_type, confidence = classify_sentence_move(sentence, llm_client)
        classified_sentences.append(
            Sentence(text=sentence, position=idx, move_type=move_type, confidence=confidence)
        )

    return AbstractAnalysisResult(sentences=classified_sentences)
