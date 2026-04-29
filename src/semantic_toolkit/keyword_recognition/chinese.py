"""Chinese scientific literature keyword extraction implementation."""

import os
import re
from typing import List

from dotenv import load_dotenv

from semantic_toolkit.keyword_recognition.models import (
    Keyword,
    KeywordExtractionResult,
    Language,
)

load_dotenv()


def _check_jieba():
    """Check if jieba is available."""
    try:
        import jieba
        return jieba
    except ImportError:
        raise ImportError(
            "jieba is not installed. Please install it with: "
            "uv add jieba"
        )


def _build_keyword_extraction_prompt(text: str, num_keywords: int = 10) -> str:
    """Build prompt for LLM keyword extraction.

    Args:
        text: Text to extract keywords from
        num_keywords: Number of keywords to extract

    Returns:
        Prompt string for LLM
    """
    prompt = f"""请从以下科技文献文本片段中提取{num_keywords}个最重要的关键词。

要求：
1. 关键词应能准确概括文献的核心内容和研究主题
2. 优先选择专业术语、技术概念和研究方法
3. 避免过于通用的词汇（如"研究"、"方法"等）
4. 关键词应为2-8个字的词组
5. 按重要性从高到低排列

文献文本：
{text}

请以JSON格式返回结果，包含关键词和置信度（0-1之间的浮点数）：
{{"keywords": [{{"text": "关键词1", "confidence": 0.95}}, {{"text": "关键词2", "confidence": 0.90}}, ...]}}

只返回JSON对象，不要包含其他文字。"""
    return prompt


def _parse_llm_keywords(response_text: str) -> List[tuple[str, float]]:
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


def _preprocess_chinese_text(text: str) -> str:
    """Preprocess Chinese text for keyword extraction.

    Args:
        text: Raw Chinese text

    Returns:
        Preprocessed text
    """
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    # Remove special characters but keep Chinese characters and common punctuation
    text = re.sub(r'[^\u4e00-\u9fff\w\s，。；：！？""''（）【】]', ' ', text)

    return text


def _get_keyword_categories(keyword: str, text: str) -> str:
    """Determine the category of a keyword based on context.

    Args:
        keyword: The keyword to categorize
        text: The original text

    Returns:
        Category string
    """
    # Simple categorization based on common patterns
    if any(char.isdigit() for char in keyword):
        return "quantitative"

    technical_patterns = ["算法", "模型", "网络", "系统", "技术", "方法", "计算", "学习", "分析"]
    for pattern in technical_patterns:
        if pattern in keyword:
            return "technical"

    concept_patterns = ["理论", "概念", "机制", "原理", "现象", "效应"]
    for pattern in concept_patterns:
        if pattern in keyword:
            return "concept"

    domain_patterns = ["医学", "生物", "化学", "物理", "工程", "数据", "信息", "计算机", "人工智能"]
    for pattern in domain_patterns:
        if pattern in keyword:
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
        if kw.text not in keyword_dict or kw.confidence > keyword_dict[kw.text].confidence:
            keyword_dict[kw.text] = kw

    return list(keyword_dict.values())


def extract_chinese_keywords(
    text: str,
    num_keywords: int = 10,
    use_segmentation: bool = True
) -> KeywordExtractionResult:
    """Extract keywords from Chinese scientific literature text.

    Args:
        text: Chinese text to extract keywords from
        num_keywords: Number of keywords to extract
        use_segmentation: Whether to use jieba segmentation for preprocessing

    Returns:
        KeywordExtractionResult containing extracted keywords and summary

    Raises:
        ValueError: If text is empty or whitespace only
        ImportError: If required packages are not installed
    """
    if not text or not text.strip():
        raise ValueError("Text cannot be empty")

    # Preprocess text
    processed_text = _preprocess_chinese_text(text)

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
                    frequency=1,
                    category=category
                )
            )
    except Exception as e:
        print(f"Error during LLM keyword extraction: {e}")

    # Fallback to jieba-based extraction if LLM fails or no keywords found
    if not keywords and use_segmentation:
        print("LLM extraction failed, falling back to segmentation-based extraction")
        jieba = _check_jieba()
        words = jieba.cut(processed_text)
        words_with_freq = [(word, processed_text.count(word)) for word in words]

        # Filter by length and common Chinese characters
        filtered_words = [
            (word, freq) for word, freq in words_with_freq
            if len(word) >= 2 and len(word) <= 8 and '\u4e00' <= word[0] <= '\u9fff'
        ]

        # Sort by frequency
        filtered_words.sort(key=lambda x: x[1], reverse=True)

        for idx, (word, freq) in enumerate(filtered_words[:num_keywords]):
            category = _get_keyword_categories(word, processed_text)
            # Calculate confidence based on frequency and position
            confidence = min(0.7 + (freq * 0.05), 0.95)
            keywords.append(
                Keyword(
                    text=word,
                    confidence=confidence,
                    position=idx,
                    frequency=freq,
                    category=category
                )
            )

    # Deduplicate keywords
    keywords = _deduplicate_keywords(keywords)

    # Sort by confidence
    keywords.sort(key=lambda x: x.confidence, reverse=True)

    return KeywordExtractionResult(keywords=keywords, language=Language.CHINESE)
