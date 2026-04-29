"""English scientific literature keyword extraction implementation."""

import os
import re
from typing import List, Tuple

from dotenv import load_dotenv

from semantic_toolkit.keyword_recognition.models import (
    Keyword,
    KeywordExtractionResult,
    Language,
)

load_dotenv()


def _check_nltk():
    """Check if nltk is available."""
    try:
        import nltk
        # Download necessary NLTK data
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt', quiet=True)
        try:
            nltk.data.find('taggers/averaged_perceptron_tagger')
        except LookupError:
            nltk.download('averaged_perceptron_tagger', quiet=True)
        return nltk
    except ImportError:
        raise ImportError(
            "nltk is not installed. Please install it with: "
            "uv add nltk"
        )


def _build_keyword_extraction_prompt(text: str, num_keywords: int = 10) -> str:
    """Build prompt for LLM keyword extraction.

    Args:
        text: Text to extract keywords from
        num_keywords: Number of keywords to extract

    Returns:
        Prompt string for LLM
    """
    prompt = f"""Extract {num_keywords} most important keywords from the following scientific literature text fragment.

Requirements:
1. Keywords should accurately summarize the core content and research topics of the literature
2. Prioritize technical terms, concepts, and research methods
3. Avoid overly common words (like "research", "method", "study", etc.)
4. Keywords can be single words or multi-word phrases
5. Include domain-specific abbreviations and acronyms when present
6. Order by importance from high to low

Literature text:
{text}

Return results in JSON format with keywords and confidence scores (float between 0 and 1):
{{"keywords": [{{"text": "keyword1", "confidence": 0.95}}, {{"text": "keyword2", "confidence": 0.90}}, ...]}}

Return only the JSON object, no additional text."""
    return prompt


def _parse_llm_keywords(response_text: str) -> List[Tuple[str, float]]:
    """Parse LLM response to extract keywords and confidence scores.

    Args:
        response_text: Raw LLM response

    Returns:
        List of (keyword, confidence) tuples
    """
    import json

    try:
        # Look for JSON pattern in the response
        json_match = re.search(r'\{[^{}]*"keywords"\s*:\s*\[[^]]*\][^{}]*\}', response_text, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
            keywords = []
            if "keywords" in result:
                for kw in result["keywords"]:
                    text = kw.get("text", "").strip()
                    confidence = float(kw.get("confidence", 0.8))
                    if text:
                        keywords.append((text, confidence))
            return keywords
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        print(f"Error parsing LLM response: {e}")

    return []


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


def _preprocess_english_text(text: str) -> str:
    """Preprocess English text for keyword extraction.

    Args:
        text: Raw English text

    Returns:
        Preprocessed text
    """
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    # Keep letters, numbers, and common punctuation
    text = re.sub(r'[^a-zA-Z0-9\s.,;:!?"\'()\[\]{}\-]', ' ', text)

    return text


def _extract_abbreviations(text: str) -> List[str]:
    """Extract abbreviations and acronyms from text.

    Args:
        text: English text

    Returns:
        List of abbreviations
    """
    # Pattern for abbreviations: uppercase letters (2-4 chars)
    abbreviations = re.findall(r'\b[A-Z]{2,4}\b', text)

    # Filter out common non-technical abbreviations
    common_non_tech = {'AND', 'OR', 'NOT', 'THE', 'AND', 'FOR', 'WITH', 'THE', 'THIS', 'THAT'}
    abbreviations = [abbr for abbr in abbreviations if abbr not in common_non_tech]

    return abbreviations


def _get_keyword_categories(keyword: str, text: str) -> str:
    """Determine the category of a keyword based on context.

    Args:
        keyword: The keyword to categorize
        text: The original text

    Returns:
        Category string
    """
    # Check if it's an abbreviation
    if keyword.isupper() and len(keyword) <= 4:
        return "abbreviation"

    # Check for numeric content
    if any(char.isdigit() for char in keyword):
        return "quantitative"

    # Technical terms patterns
    technical_patterns = [
        "algorithm", "model", "network", "system", "technique", "method",
        "computation", "learning", "analysis", "architecture", "framework",
        "protocol", "interface", "platform", "engine"
    ]
    keyword_lower = keyword.lower()
    for pattern in technical_patterns:
        if pattern in keyword_lower:
            return "technical"

    # Concept patterns
    concept_patterns = [
        "theory", "concept", "mechanism", "principle", "phenomenon", "effect",
        "hypothesis", "paradigm", "approach", "strategy"
    ]
    for pattern in concept_patterns:
        if pattern in keyword_lower:
            return "concept"

    # Domain patterns
    domain_patterns = [
        "medical", "biological", "chemical", "physical", "engineering",
        "data", "information", "computer", "artificial intelligence",
        "machine learning", "neural", "quantum", "statistical"
    ]
    for pattern in domain_patterns:
        if pattern in keyword_lower:
            return "domain"

    return "general"


def _deduplicate_keywords(keywords: List[Keyword]) -> List[Keyword]:
    """Remove duplicate keywords, keeping the one with higher confidence.

    Args:
        keywords: List of keywords

    Returns:
        Deduplicated list
    """
    keyword_dict = {}
    for kw in keywords:
        key_lower = kw.text.lower()
        if key_lower not in keyword_dict or kw.confidence > keyword_dict[key_lower].confidence:
            keyword_dict[key_lower] = kw

    return list(keyword_dict.values())


def _extract_pos_based_keywords(text: str, num_keywords: int) -> List[Tuple[str, float]]:
    """Extract keywords using POS tagging as fallback.

    Args:
        text: Preprocessed text
        num_keywords: Number of keywords to extract

    Returns:
        List of (keyword, confidence) tuples
    """
    try:
        nltk = _check_nltk()
        from collections import Counter

        # Tokenize and get POS tags
        tokens = nltk.word_tokenize(text)
        pos_tags = nltk.pos_tag(tokens)

        # Filter for nouns (NN, NNS, NNP, NNPS) and technical terms
        noun_tags = {'NN', 'NNS', 'NNP', 'NNPS'}
        candidate_words = [
            word.lower() for word, pos in pos_tags
            if pos in noun_tags and len(word) > 2 and word.isalpha()
        ]

        # Count frequency
        word_freq = Counter(candidate_words)

        # Get top words
        top_words = word_freq.most_common(num_keywords)

        # Assign confidence based on frequency and length
        keywords = []
        for word, freq in top_words:
            # Longer words and more frequent words get higher confidence
            confidence = min(0.6 + (len(word) * 0.02) + (freq * 0.03), 0.9)
            keywords.append((word, confidence))

        return keywords

    except Exception as e:
        print(f"Error in POS-based extraction: {e}")
        return []


def extract_english_keywords(
    text: str,
    num_keywords: int = 10,
    use_pos_tagging: bool = True
) -> KeywordExtractionResult:
    """Extract keywords from English scientific literature text.

    Args:
        text: English text to extract keywords from
        num_keywords: Number of keywords to extract
        use_pos_tagging: Whether to use NLTK POS tagging for preprocessing/fallback

    Returns:
        KeywordExtractionResult containing extracted keywords and summary

    Raises:
        ValueError: If text is empty or whitespace only
        ImportError: If required packages are not installed
    """
    if not text or not text.strip():
        raise ValueError("Text cannot be empty")

    # Preprocess text
    processed_text = _preprocess_english_text(text)

    if not processed_text:
        raise ValueError("Could not process the provided text")

    keywords = []

    # Use LLM for keyword extraction
    llm_client = _get_llm_client()
    prompt = _build_keyword_extraction_prompt(processed_text, num_keywords)

    try:
        response = llm_client.generate(prompt)
        llm_keywords = _parse_llm_keywords(response)

        # Create Keyword objects
        for idx, (kw_text, confidence) in enumerate(llm_keywords):
            category = _get_keyword_categories(kw_text, processed_text)
            keywords.append(
                Keyword(
                    text=kw_text,
                    confidence=confidence,
                    position=idx,
                    frequency=processed_text.lower().count(kw_text.lower()),
                    category=category
                )
            )
    except Exception as e:
        print(f"Error during LLM keyword extraction: {e}")

    # If no keywords from LLM or as supplement, extract abbreviations
    abbreviations = _extract_abbreviations(processed_text)
    for idx, abbr in enumerate(abbreviations[:num_keywords // 2]):
        keywords.append(
            Keyword(
                text=abbr,
                confidence=0.85,
                position=len(keywords),
                frequency=processed_text.count(abbr),
                category="abbreviation"
            )
        )

    # Fallback to POS-based extraction if needed
    if not keywords and use_pos_tagging:
        print("LLM extraction failed, falling back to POS-based extraction")
        pos_keywords = _extract_pos_based_keywords(processed_text, num_keywords)

        for idx, (word, confidence) in enumerate(pos_keywords):
            category = _get_keyword_categories(word, processed_text)
            keywords.append(
                Keyword(
                    text=word,
                    confidence=confidence,
                    position=idx,
                    frequency=processed_text.lower().count(word),
                    category=category
                )
            )

    # Deduplicate keywords
    keywords = _deduplicate_keywords(keywords)

    # Sort by confidence
    keywords.sort(key=lambda x: x.confidence, reverse=True)

    return KeywordExtractionResult(keywords=keywords, language=Language.ENGLISH)
