"""Tests for keyword recognition module."""

import pytest
from unittest.mock import Mock, patch

from semantic_toolkit.keyword_recognition import (
    extract_chinese_keywords,
    extract_english_keywords,
    extract_keywords,
    Keyword,
    KeywordExtractionResult,
    Language,
)


class TestKeywordExtractionModels:
    """Tests for data models."""

    def test_keyword_creation(self):
        """Test Keyword object creation."""
        keyword = Keyword(
            text="deep learning",
            confidence=0.95,
            position=1,
            frequency=3,
            category="technical"
        )

        assert keyword.text == "deep learning"
        assert keyword.confidence == 0.95
        assert keyword.position == 1
        assert keyword.frequency == 3
        assert keyword.category == "technical"

    def test_keyword_repr(self):
        """Test Keyword string representation."""
        keyword = Keyword(
            text="AI",
            confidence=0.88,
            position=0,
            category="domain"
        )
        repr_str = repr(keyword)

        assert "AI" in repr_str
        assert "0.88" in repr_str
        assert "technical" not in repr_str  # Should use actual category

    def test_keyword_equality(self):
        """Test Keyword equality based on text."""
        kw1 = Keyword(text="algorithm", confidence=0.9)
        kw2 = Keyword(text="algorithm", confidence=0.8)
        kw3 = Keyword(text="model", confidence=0.9)

        assert kw1 == kw2  # Same text
        assert kw1 != kw3  # Different text

    def test_keyword_hash(self):
        """Test Keyword hash for use in sets."""
        kw1 = Keyword(text="neural", confidence=0.9)
        kw2 = Keyword(text="neural", confidence=0.8)
        kw3 = Keyword(text="network", confidence=0.9)

        keyword_set = {kw1, kw2, kw3}
        # Should only have 2 unique keywords based on text
        assert len(keyword_set) == 2

    def test_language_enum(self):
        """Test Language enum values."""
        assert str(Language.CHINESE) == "chinese"
        assert str(Language.ENGLISH) == "english"

    def test_keyword_extraction_result_creation(self):
        """Test KeywordExtractionResult creation."""
        keywords = [
            Keyword(text="AI", confidence=0.95, position=0),
            Keyword(text="ML", confidence=0.90, position=1),
        ]
        result = KeywordExtractionResult(keywords, Language.ENGLISH)

        assert result.language == Language.ENGLISH
        assert len(result.keywords) == 2
        assert result.summary["total_keywords"] == 2
        assert result.summary["average_confidence"] == 0.925

    def test_empty_keyword_result(self):
        """Test KeywordExtractionResult with no keywords."""
        result = KeywordExtractionResult([], Language.CHINESE)

        assert result.summary["total_keywords"] == 0
        assert result.summary["average_confidence"] == 0.0
        assert result.summary["categories"] == {}

    def test_get_keywords_by_category(self):
        """Test filtering keywords by category."""
        keywords = [
            Keyword(text="CNN", confidence=0.9, category="technical"),
            Keyword(text="deep learning", confidence=0.95, category="technical"),
            Keyword(text="theory", confidence=0.8, category="concept"),
        ]
        result = KeywordExtractionResult(keywords, Language.ENGLISH)

        technical_keywords = result.get_keywords_by_category("technical")
        assert len(technical_keywords) == 2
        assert all(kw.category == "technical" for kw in technical_keywords)

    def test_get_top_keywords(self):
        """Test getting top N keywords."""
        keywords = [
            Keyword(text="model", confidence=0.7, frequency=1),
            Keyword(text="algorithm", confidence=0.95, frequency=5),
            Keyword(text="system", confidence=0.85, frequency=3),
        ]
        result = KeywordExtractionResult(keywords, Language.ENGLISH)

        top_2 = result.get_top_keywords(2)
        assert len(top_2) == 2
        assert top_2[0].text == "algorithm"  # Highest confidence + frequency
        assert top_2[1].text == "system"


class TestChineseKeywordExtraction:
    """Tests for Chinese keyword extraction."""

    def test_empty_text_raises_error(self):
        """Test that empty text raises ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            extract_chinese_keywords("")

    def test_whitespace_only_text_raises_error(self):
        """Test that whitespace-only text raises ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            extract_chinese_keywords("   \n\t  ")

    @patch('semantic_toolkit.keyword_recognition.chinese._get_llm_client')
    def test_chinese_keyword_extraction_with_mock(self, mock_get_llm):
        """Test Chinese keyword extraction with mocked LLM."""
        mock_client = Mock()
        mock_client.generate.return_value = '''{
            "keywords": [
                {"text": "深度学习", "confidence": 0.95},
                {"text": "神经网络", "confidence": 0.90},
                {"text": "算法优化", "confidence": 0.88}
            ]
        }'''
        mock_get_llm.return_value = mock_client

        text = "这项研究提出了一种基于深度学习的神经网络算法优化方法。"
        result = extract_chinese_keywords(text, num_keywords=3, use_segmentation=False)

        assert result.language == Language.CHINESE
        assert result.summary["total_keywords"] >= 1
        assert result.summary["average_confidence"] > 0

    @patch('semantic_toolkit.keyword_recognition.chinese._check_jieba')
    def test_fallback_to_segmentation(self, mock_jieba):
        """Test fallback to segmentation when LLM fails."""
        # Mock jieba to return specific words
        mock_jieba_instance = Mock()
        mock_jieba_instance.cut.return_value = ["深度学习", "研究", "算法", "优化"]
        mock_jieba.return_value = mock_jieba_instance

        # Mock LLM client to raise exception
        mock_llm_client = Mock()
        mock_llm_client.generate.side_effect = Exception("LLM unavailable")

        with patch('semantic_toolkit.keyword_recognition.chinese._get_llm_client', return_value=mock_llm_client):
            text = "深度学习研究算法优化"

            # This should work even if jieba isn't installed in test environment
            # by using the mock
            try:
                result = extract_chinese_keywords(text, num_keywords=3, use_segmentation=True)
                assert result.language == Language.CHINESE
            except ImportError:
                # Expected if jieba is not installed
                pass


class TestEnglishKeywordExtraction:
    """Tests for English keyword extraction."""

    def test_empty_text_raises_error(self):
        """Test that empty text raises ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            extract_english_keywords("")

    def test_whitespace_only_text_raises_error(self):
        """Test that whitespace-only text raises ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            extract_english_keywords("   \n\t  ")

    @patch('semantic_toolkit.keyword_recognition.english._get_llm_client')
    def test_english_keyword_extraction_with_mock(self, mock_get_llm):
        """Test English keyword extraction with mocked LLM."""
        mock_client = Mock()
        mock_client.generate.return_value = '''{
            "keywords": [
                {"text": "deep learning", "confidence": 0.95},
                {"text": "neural networks", "confidence": 0.92},
                {"text": "algorithm optimization", "confidence": 0.88}
            ]
        }'''
        mock_get_llm.return_value = mock_client

        text = "This study proposes a novel deep learning algorithm for neural networks optimization."
        result = extract_english_keywords(text, num_keywords=3, use_pos_tagging=False)

        assert result.language == Language.ENGLISH
        assert result.summary["total_keywords"] >= 1
        assert result.summary["average_confidence"] > 0

    def test_abbreviation_extraction(self):
        """Test extraction of abbreviations from text."""
        from semantic_toolkit.keyword_recognition.english import _extract_abbreviations

        text = "This CNN system uses AI and ML algorithms. The API provides access to GPU resources."
        abbreviations = _extract_abbreviations(text)

        assert "CNN" in abbreviations
        assert "AI" in abbreviations
        assert "ML" in abbreviations
        assert "API" in abbreviations
        assert "GPU" in abbreviations


class TestUnifiedKeywordExtraction:
    """Tests for unified keyword extraction interface."""

    @patch('semantic_toolkit.keyword_recognition.chinese._check_jieba')
    def test_unified_chinese_extraction(self, mock_jieba):
        """Test unified interface for Chinese text."""
        # Mock jieba to return specific words
        mock_jieba_instance = Mock()
        mock_jieba_instance.cut.return_value = ["深度学习", "算法", "研究"]
        mock_jieba.return_value = mock_jieba_instance

        # Mock LLM client to raise exception
        mock_llm_client = Mock()
        mock_llm_client.generate.side_effect = Exception("LLM unavailable")

        with patch('semantic_toolkit.keyword_recognition.chinese._get_llm_client', return_value=mock_llm_client):
            text = "深度学习算法研究"
            result = extract_keywords(text, language=Language.CHINESE)

            assert result.language == Language.CHINESE

    @patch('semantic_toolkit.keyword_recognition.english._check_nltk')
    def test_unified_english_extraction(self, mock_nltk):
        """Test unified interface for English text."""
        # Mock nltk to return specific tokens
        mock_nltk_instance = Mock()
        mock_nltk_instance.word_tokenize.return_value = ["Deep", "learning", "algorithm", "research"]
        mock_nltk_instance.pos_tag.return_value = [
            ("Deep", "NNP"), ("learning", "NN"), ("algorithm", "NN"), ("research", "NN")
        ]
        mock_nltk.data.find.return_value = True  # Simulate NLTK data exists
        mock_nltk.return_value = mock_nltk_instance

        # Mock LLM client to raise exception
        mock_llm_client = Mock()
        mock_llm_client.generate.side_effect = Exception("LLM unavailable")

        with patch('semantic_toolkit.keyword_recognition.english._get_llm_client', return_value=mock_llm_client):
            text = "Deep learning algorithm research"
            result = extract_keywords(text, language=Language.ENGLISH)

            assert result.language == Language.ENGLISH

    def test_invalid_language_raises_error(self):
        """Test that invalid language raises ValueError."""
        text = "Some text"
        with pytest.raises(ValueError, match="Unsupported language"):
            extract_keywords(text, language="invalid")

    @patch('semantic_toolkit.keyword_recognition.english._check_nltk')
    def test_default_language_is_english(self, mock_nltk):
        """Test that default language is English."""
        # Mock nltk to return specific tokens
        mock_nltk_instance = Mock()
        mock_nltk_instance.word_tokenize.return_value = ["Machine", "learning", "research"]
        mock_nltk_instance.pos_tag.return_value = [
            ("Machine", "NN"), ("learning", "NN"), ("research", "NN")
        ]
        mock_nltk.data.find.return_value = True  # Simulate NLTK data exists
        mock_nltk.return_value = mock_nltk_instance

        # Mock LLM client to raise exception
        mock_llm_client = Mock()
        mock_llm_client.generate.side_effect = Exception("LLM unavailable")

        with patch('semantic_toolkit.keyword_recognition.english._get_llm_client', return_value=mock_llm_client):
            text = "Machine learning research"
            result = extract_keywords(text)

            assert result.language == Language.ENGLISH

    def test_unified_empty_text_raises_error(self):
        """Test that empty text raises ValueError in unified interface."""
        with pytest.raises(ValueError, match="cannot be empty"):
            extract_keywords("")


class TestTextPreprocessing:
    """Tests for text preprocessing functions."""

    def test_chinese_text_preprocessing(self):
        """Test Chinese text preprocessing."""
        from semantic_toolkit.keyword_recognition.chinese import _preprocess_chinese_text

        text = "   多个  空格  的  文本   "
        processed = _preprocess_chinese_text(text)

        assert processed == "多个 空格 的 文本"
        assert "  " not in processed

    def test_english_text_preprocessing(self):
        """Test English text preprocessing."""
        from semantic_toolkit.keyword_recognition.english import _preprocess_english_text

        text = "   Multiple   spaces   in   text   "
        processed = _preprocess_english_text(text)

        assert processed == "Multiple spaces in text"
        assert "  " not in processed

    def test_chinese_special_chars_removal(self):
        """Test removal of special characters in Chinese text."""
        from semantic_toolkit.keyword_recognition.chinese import _preprocess_chinese_text

        text = "中文文本@#$%^&*()测试"
        processed = _preprocess_chinese_text(text)

        assert "@" not in processed
        assert "#" not in processed
        assert "中文文本" in processed
        assert "测试" in processed


class TestKeywordCategorization:
    """Tests for keyword categorization."""

    def test_chinese_keyword_categorization(self):
        """Test Chinese keyword categorization."""
        from semantic_toolkit.keyword_recognition.chinese import _get_keyword_categories

        text = "深度学习算法模型系统"

        assert _get_keyword_categories("算法", text) == "technical"
        assert _get_keyword_categories("模型", text) == "technical"

    def test_english_keyword_categorization(self):
        """Test English keyword categorization."""
        from semantic_toolkit.keyword_recognition.english import _get_keyword_categories

        text = "deep learning algorithm neural network model system"

        assert _get_keyword_categories("algorithm", text) == "technical"
        assert _get_keyword_categories("model", text) == "technical"
        assert _get_keyword_categories("CNN", text) == "abbreviation"

    def test_abbreviation_categorization(self):
        """Test abbreviation categorization in English."""
        from semantic_toolkit.keyword_recognition.english import _get_keyword_categories

        assert _get_keyword_categories("CNN", "any text") == "abbreviation"
        assert _get_keyword_categories("GPU", "any text") == "abbreviation"


class TestKeywordDeduplication:
    """Tests for keyword deduplication."""

    def test_deduplicate_keywords(self):
        """Test keyword deduplication keeps higher confidence."""
        from semantic_toolkit.keyword_recognition.english import _deduplicate_keywords

        keywords = [
            Keyword(text="algorithm", confidence=0.7),
            Keyword(text="algorithm", confidence=0.9),
            Keyword(text="model", confidence=0.8),
            Keyword(text="ALGORITHM", confidence=0.85),  # Different case
        ]

        deduplicated = _deduplicate_keywords(keywords)

        # Should have 2 unique keywords (algorithm/ALGORITHM and model)
        assert len(deduplicated) == 2
        # algorithm should have confidence 0.9 (highest)
        algo_kw = next(kw for kw in deduplicated if kw.text.lower() == "algorithm")
        assert algo_kw.confidence == 0.9


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
