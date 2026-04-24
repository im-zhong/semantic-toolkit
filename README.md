# Semantic Toolkit

A semantic computing toolkit for scientific literature analysis that provides automated move recognition and keyword extraction for Chinese and English research texts using LLM-powered classification.

## Features

### Move Recognition
- **Automatic Move Recognition**: Classifies sentences in research abstracts into five semantic moves:
  - **BACKGROUND** (研究背景): Context, problem statement, or knowledge gap
  - **PURPOSE** (研究目的): Objectives, goals, or hypotheses
  - **METHODS** (研究方法): Methodology, procedures, or experimental design
  - **RESULTS** (研究结果): Main findings, data, or outcomes
  - **CONCLUSIONS** (研究结论): Implications, interpretations, or recommendations

### Keyword Extraction
- **Automatic Keyword Extraction**: Extracts key terms from scientific literature:
  - **Chinese Literature**: Handles Chinese text with proper segmentation and categorization
  - **English Literature**: Supports English text with technical term and abbreviation recognition
  - **Smart Categorization**: Classifies keywords by type (technical, conceptual, domain-specific, etc.)
  - **Confidence Scoring**: Provides confidence scores for each extracted keyword
  - **Fallback Mechanisms**: Uses rule-based extraction when LLM is unavailable

### General Features
- **LLM-Powered**: Uses Zhipu AI's GLM models for accurate classification and extraction
- **Structured Output**: Provides confidence scores, categories, and summary statistics
- **Easy Integration**: Simple Python API for seamless integration
- **Bilingual Support**: Full support for Chinese and English scientific literature

## Installation

### Using uv (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd semantic-toolkit

# Install dependencies
uv sync

# For development dependencies
uv sync --extra dev
```

### Configuration

1. Copy the environment template:
```bash
cp .env.example .env
```

2. Edit `.env` and add your Zhipu AI API key:
```bash
ZHIPU_API_KEY=your-api-key-here
```

Get your API key from [https://open.bigmodel.cn/](https://open.bigmodel.cn/)

## Usage

### Move Recognition Example

```python
from semantic_toolkit.move_recognition import analyze_english_abstract

abstract = """
This study addresses the growing need for efficient data processing.
We aim to develop a novel algorithm for large-scale data analysis.
The proposed method combines deep learning with traditional statistical approaches.
Results show a 40% improvement in processing speed.
These findings suggest significant potential for real-world applications.
"""

result = analyze_english_abstract(abstract)

# Print summary
print(f"Total sentences: {result.summary['total_sentences']}")
print(f"Move counts: {result.summary['move_counts']}")

# Access individual sentences
for sentence in result.sentences:
    print(f"{sentence.move_type.value}: {sentence.text} (confidence: {sentence.confidence:.2f})")
```

### Keyword Extraction Examples

#### Chinese Keyword Extraction

```python
from semantic_toolkit.keyword_recognition import extract_chinese_keywords

chinese_text = """
本研究提出了一种基于深度学习的图像识别算法。
该算法采用卷积神经网络作为基础架构，通过改进的激活函数
和优化策略，显著提升了图像分类的准确率。
"""

result = extract_chinese_keywords(
    text=chinese_text,
    num_keywords=10,
    use_segmentation=True
)

# Print summary
print(f"Total keywords: {result.summary['total_keywords']}")
print(f"Average confidence: {result.summary['average_confidence']:.2f}")
print(f"Categories: {result.summary['categories']}")

# Access individual keywords
for keyword in result.get_top_keywords(10):
    print(f"{keyword.text:20} (confidence: {keyword.confidence:.2f}, category: {keyword.category})")
```

#### English Keyword Extraction

```python
from semantic_toolkit.keyword_recognition import extract_english_keywords

english_text = """
This paper presents a novel deep learning approach for image recognition.
The proposed algorithm utilizes convolutional neural networks with improved
activation functions and optimization strategies, significantly improving
classification accuracy.
"""

result = extract_english_keywords(
    text=english_text,
    num_keywords=10,
    use_pos_tagging=True
)

# Print summary
print(f"Total keywords: {result.summary['total_keywords']}")
print(f"Average confidence: {result.summary['average_confidence']:.2f}")

# Get keywords by category
technical_keywords = result.get_keywords_by_category("technical")
for keyword in technical_keywords:
    print(f"Technical: {keyword.text} (confidence: {keyword.confidence:.2f})")

# Get abbreviations
abbreviations = result.get_keywords_by_category("abbreviation")
for keyword in abbreviations:
    print(f"Abbreviation: {keyword.text} (confidence: {keyword.confidence:.2f})")
```

#### Unified Interface

```python
from semantic_toolkit.keyword_recognition import extract_keywords, Language

# Extract keywords from Chinese text
chinese_result = extract_keywords(
    text="机器学习算法在医疗诊断中的应用研究",
    language=Language.CHINESE,
    num_keywords=5
)

# Extract keywords from English text (default)
english_result = extract_keywords(
    text="Machine learning algorithms for medical diagnosis",
    language=Language.ENGLISH,
    num_keywords=5
)

# Access results
for keyword in english_result.keywords:
    print(f"{keyword.text}: {keyword.confidence:.2f}")
```

### Expected Output

```
Total sentences: 5
Move counts: {'BACKGROUND': 1, 'PURPOSE': 1, 'METHODS': 1, 'RESULTS': 1, 'CONCLUSIONS': 1}
BACKGROUND: This study addresses the growing need for efficient data processing. (confidence: 0.95)
PURPOSE: We aim to develop a novel algorithm for large-scale data analysis. (confidence: 0.90)
METHODS: The proposed method combines deep learning with traditional statistical approaches. (confidence: 0.88)
RESULTS: Results show a 40% improvement in processing speed. (confidence: 0.92)
CONCLUSIONS: These findings suggest significant potential for real-world applications. (confidence: 0.89)
```

## API Reference

### Move Recognition

#### `analyze_english_abstract(text: str) -> AbstractAnalysisResult`

Main function to analyze an English abstract.

**Parameters:**
- `text` (str): The abstract text to analyze

**Returns:**
- `AbstractAnalysisResult`: Object containing sentence classifications and summary

**Raises:**
- `ValueError`: If text is empty or cannot be processed
- `ImportError`: If zai-sdk is not installed

#### `split_into_sentences(text: str) -> List[str]`

Split abstract text into sentences.

**Parameters:**
- `text` (str): Text to split

**Returns:**
- `List[str]`: List of sentences

### Keyword Extraction

#### `extract_chinese_keywords(text: str, num_keywords: int = 10, use_segmentation: bool = True) -> KeywordExtractionResult`

Extract keywords from Chinese scientific literature.

**Parameters:**
- `text` (str): Chinese text to extract keywords from
- `num_keywords` (int, optional): Number of keywords to extract. Default: 10
- `use_segmentation` (bool, optional): Whether to use jieba segmentation for preprocessing. Default: True

**Returns:**
- `KeywordExtractionResult`: Object containing extracted keywords and summary

**Raises:**
- `ValueError`: If text is empty
- `ImportError`: If required packages are not installed

#### `extract_english_keywords(text: str, num_keywords: int = 10, use_pos_tagging: bool = True) -> KeywordExtractionResult`

Extract keywords from English scientific literature.

**Parameters:**
- `text` (str): English text to extract keywords from
- `num_keywords` (int, optional): Number of keywords to extract. Default: 10
- `use_pos_tagging` (bool, optional): Whether to use NLTK POS tagging for preprocessing. Default: True

**Returns:**
- `KeywordExtractionResult`: Object containing extracted keywords and summary

**Raises:**
- `ValueError`: If text is empty
- `ImportError`: If required packages are not installed

#### `extract_keywords(text: str, language: Language = Language.ENGLISH, num_keywords: int = 10, **kwargs) -> KeywordExtractionResult`

Unified interface for keyword extraction that automatically dispatches to language-specific functions.

**Parameters:**
- `text` (str): Text to extract keywords from
- `language` (Language, optional): Language of the text (chinese or english). Default: Language.ENGLISH
- `num_keywords` (int, optional): Number of keywords to extract. Default: 10
- `**kwargs`: Additional arguments passed to language-specific functions

**Returns:**
- `KeywordExtractionResult`: Object containing extracted keywords and summary

**Raises:**
- `ValueError`: If text is empty or language is invalid
- `ImportError`: If required packages are not installed

### Data Models

#### Move Recognition Models

##### `Sentence`
- `text`: Original sentence text
- `position`: Index in the abstract (0-based)
- `move_type`: `MoveType` enum value
- `confidence`: Classification confidence (0.0 - 1.0)

##### `AbstractAnalysisResult`
- `sentences`: List of `Sentence` objects
- `summary`: Dictionary with total sentence count and move counts

##### `MoveType` (Enum)
- `BACKGROUND`
- `PURPOSE`
- `METHODS`
- `RESULTS`
- `CONCLUSIONS`

#### Keyword Extraction Models

##### `Keyword`
- `text`: Keyword text
- `confidence`: Extraction confidence (0.0 - 1.0)
- `position`: Position in extraction order (0-based)
- `frequency`: Frequency of keyword in text
- `category`: Keyword category (technical, concept, domain, general, abbreviation)

##### `KeywordExtractionResult`
- `keywords`: List of `Keyword` objects
- `language`: `Language` enum value
- `summary`: Dictionary with statistics

**Methods:**
- `get_keywords_by_category(category: str) -> List[Keyword]`: Filter keywords by category
- `get_top_keywords(n: int = 10) -> List[Keyword]`: Get top N keywords by confidence and frequency

##### `Language` (Enum)
- `CHINESE`
- `ENGLISH`

## Development

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=semantic_toolkit --cov-report=html

# Run specific test file
uv run pytest tests/test_english_abstract.py
uv run pytest tests/test_keyword_recognition.py
```

### Running Examples

```bash
# Run move recognition examples
uv run python example.py

# Run keyword extraction examples
uv run python example_keyword.py
```

### Project Structure

```
semantic-toolkit/
├── src/
│   └── semantic_toolkit/
│       ├── __init__.py
│       ├── move_recognition/         # Move recognition module
│       │   ├── __init__.py
│       │   ├── models.py            # Data models for move recognition
│       │   └── english_abstract.py  # English abstract analysis
│       └── keyword_recognition/     # Keyword extraction module
│           ├── __init__.py
│           ├── models.py            # Data models for keywords
│           ├── chinese.py           # Chinese keyword extraction
│           └── english.py           # English keyword extraction
├── tests/
│   ├── __init__.py
│   ├── test_english_abstract.py     # Move recognition tests
│   └── test_keyword_recognition.py # Keyword extraction tests
├── example.py                       # Move recognition examples
├── example_keyword.py               # Keyword extraction examples
├── pyproject.toml                   # Project configuration
├── .env.example                     # Environment template
└── README.md                        # This file
```

## Environment Variables

- `ZHIPU_API_KEY` (required): Your Zhipu AI API key
- `ZHIPU_MODEL` (optional): Model to use (default: `glm-4`)

## License

[Add your license here]

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- Zhipu AI for providing the GLM language models
- The academic community for research on move analysis in abstracts
