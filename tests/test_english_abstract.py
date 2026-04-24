"""Test suite for English abstract move recognition."""

import pytest
from unittest.mock import Mock, patch

from semantic_toolkit.move_recognition import (
    analyze_english_abstract,
    AbstractAnalysisResult,
    MoveType,
    Sentence,
)
from semantic_toolkit.move_recognition.english_abstract import (
    split_into_sentences,
    _build_classification_prompt,
    _parse_llm_response,
    classify_sentence_move,
)


class TestSentenceSplitting:
    """Test sentence splitting functionality."""

    def test_split_empty_text(self):
        """Test splitting empty text."""
        assert split_into_sentences("") == []
        assert split_into_sentences("   ") == []

    def test_split_single_sentence(self):
        """Test splitting a single sentence."""
        text = "This is a single sentence."
        result = split_into_sentences(text)
        assert len(result) == 1
        assert result[0] == text

    def test_split_multiple_sentences(self):
        """Test splitting multiple sentences."""
        text = "First sentence. Second sentence. Third sentence."
        result = split_into_sentences(text)
        assert len(result) == 3
        assert result[0] == "First sentence."
        assert result[1] == "Second sentence."
        assert result[2] == "Third sentence."

    def test_split_with_extra_whitespace(self):
        """Test splitting text with extra whitespace."""
        text = "  First sentence.  Second sentence.  "
        result = split_into_sentences(text)
        assert len(result) == 2
        assert result[0] == "First sentence."
        assert result[1] == "Second sentence."


class TestPromptBuilding:
    """Test prompt building for LLM classification."""

    def test_build_prompt_includes_move_descriptions(self):
        """Test that prompt includes move type descriptions."""
        prompt = _build_classification_prompt("Test sentence.")
        assert "BACKGROUND" in prompt
        assert "PURPOSE" in prompt
        assert "METHODS" in prompt
        assert "RESULTS" in prompt
        assert "CONCLUSIONS" in prompt

    def test_build_prompt_includes_examples(self):
        """Test that prompt includes few-shot examples."""
        prompt = _build_classification_prompt("Test sentence.")
        assert "Examples:" in prompt
        assert "Classification:" in prompt

    def test_build_prompt_includes_target_sentence(self):
        """Test that prompt includes the target sentence."""
        sentence = "This is the sentence to classify."
        prompt = _build_classification_prompt(sentence)
        assert sentence in prompt


class TestResponseParsing:
    """Test LLM response parsing."""

    def test_parse_json_response(self):
        """Test parsing a valid JSON response."""
        response = '{"move_type": "METHODS", "confidence": 0.95}'
        move_type, confidence = _parse_llm_response(response)
        assert move_type == MoveType.METHODS
        assert confidence == 0.95

    def test_parse_json_with_text_around(self):
        """Test parsing JSON with surrounding text."""
        response = 'Some text {"move_type": "BACKGROUND", "confidence": 0.85} more text'
        move_type, confidence = _parse_llm_response(response)
        assert move_type == MoveType.BACKGROUND
        assert confidence == 0.85

    def test_parse_fallback_move_type(self):
        """Test fallback to move type detection when JSON parsing fails."""
        response = "This is clearly about METHODS and procedures."
        move_type, confidence = _parse_llm_response(response)
        assert move_type == MoveType.METHODS
        assert confidence == 0.7

    def test_parse_default_fallback(self):
        """Test default fallback when no move type is found."""
        response = "This is some unparseable text."
        move_type, confidence = _parse_llm_response(response)
        assert move_type == MoveType.BACKGROUND
        assert confidence == 0.5


class TestMoveClassification:
    """Test move classification with mocked LLM."""

    @patch("semantic_toolkit.move_recognition.english_abstract._get_llm_client")
    def test_classify_sentence_with_mock(self, mock_get_client):
        """Test sentence classification with mocked LLM client."""
        mock_client = Mock()
        mock_client.generate.return_value = '{"move_type": "RESULTS", "confidence": 0.92}'
        mock_get_client.return_value = mock_client

        move_type, confidence = classify_sentence_move("This shows improved results.", mock_client)

        assert move_type == MoveType.RESULTS
        assert confidence == 0.92

    @patch("semantic_toolkit.move_recognition.english_abstract._get_llm_client")
    def test_classify_sentence_error_handling(self, mock_get_client):
        """Test error handling in sentence classification."""
        mock_client = Mock()
        mock_client.generate.side_effect = Exception("API error")
        mock_get_client.return_value = mock_client

        move_type, confidence = classify_sentence_move("Test sentence.", mock_client)

        assert move_type == MoveType.BACKGROUND
        assert confidence == 0.0


class TestAbstractAnalysis:
    """Test full abstract analysis."""

    @patch("semantic_toolkit.move_recognition.english_abstract._get_llm_client")
    def test_analyze_abstract_valid_text(self, mock_get_client):
        """Test analyzing a valid abstract."""
        mock_client = Mock()
        mock_client.generate.side_effect = [
            '{"move_type": "BACKGROUND", "confidence": 0.95}',
            '{"move_type": "PURPOSE", "confidence": 0.90}',
            '{"move_type": "METHODS", "confidence": 0.88}',
            '{"move_type": "RESULTS", "confidence": 0.92}',
            '{"move_type": "CONCLUSIONS", "confidence": 0.89}',
        ]
        mock_get_client.return_value = mock_client

        abstract = """This study addresses the growing need for efficient data processing.
        We aim to develop a novel algorithm for large-scale data analysis.
        The proposed method combines deep learning with traditional statistical approaches.
        Results show a 40% improvement in processing speed.
        These findings suggest significant potential for real-world applications."""

        result = analyze_english_abstract(abstract)

        assert isinstance(result, AbstractAnalysisResult)
        assert result.summary["total_sentences"] == 5
        assert result.summary["move_counts"]["BACKGROUND"] == 1
        assert result.summary["move_counts"]["PURPOSE"] == 1
        assert result.summary["move_counts"]["METHODS"] == 1
        assert result.summary["move_counts"]["RESULTS"] == 1
        assert result.summary["move_counts"]["CONCLUSIONS"] == 1

    def test_analyze_abstract_empty_text(self):
        """Test analyzing empty text raises error."""
        with pytest.raises(ValueError, match="Abstract text cannot be empty"):
            analyze_english_abstract("")

    def test_analyze_abstract_whitespace_only(self):
        """Test analyzing whitespace-only text raises error."""
        with pytest.raises(ValueError, match="Abstract text cannot be empty"):
            analyze_english_abstract("   \n   ")

    def test_analyze_abstract_without_api_key(self):
        """Test analysis fails without API key."""
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="ZHIPU_API_KEY"):
                analyze_english_abstract("Valid abstract text.")


class TestDataModels:
    """Test data models."""

    def test_sentence_creation(self):
        """Test creating a Sentence object."""
        sentence = Sentence(
            text="This is a test sentence.",
            position=0,
            move_type=MoveType.RESULTS,
            confidence=0.95,
        )
        assert sentence.text == "This is a test sentence."
        assert sentence.position == 0
        assert sentence.move_type == MoveType.RESULTS
        assert sentence.confidence == 0.95

    def test_abstract_analysis_result_creation(self):
        """Test creating AbstractAnalysisResult."""
        sentences = [
            Sentence("First sentence.", 0, MoveType.BACKGROUND, 0.95),
            Sentence("Second sentence.", 1, MoveType.PURPOSE, 0.90),
        ]
        result = AbstractAnalysisResult(sentences)
        assert result.summary["total_sentences"] == 2
        assert result.summary["move_counts"]["BACKGROUND"] == 1
        assert result.summary["move_counts"]["PURPOSE"] == 1

    def test_move_type_enum(self):
        """Test MoveType enum."""
        assert MoveType.BACKGROUND.value == "BACKGROUND"
        assert MoveType.PURPOSE.value == "PURPOSE"
        assert MoveType.METHODS.value == "METHODS"
        assert MoveType.RESULTS.value == "RESULTS"
        assert MoveType.CONCLUSIONS.value == "CONCLUSIONS"
