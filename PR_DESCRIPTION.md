## Summary
Add comprehensive keyword recognition functionality with FastAPI REST API support for Chinese and English scientific literature.

**Note**: This PR focuses solely on backend API implementation. Frontend integration is not included in this scope.

## 🎯 Features

**Backend-Only Implementation**: This PR provides a complete REST API for keyword recognition. Frontend integration is out of scope and should be handled in a separate PR.

### Keyword Recognition Tool
- **Chinese Keyword Extraction**: Intelligent extraction using LLM with jieba segmentation support
- **English Keyword Extraction**: Advanced extraction with NLTK POS tagging support  
- **Smart Categorization**: Automatic classification into technical, concept, domain, abbreviation, general, quantitative categories
- **Confidence Scoring**: Quality assessment for each extracted keyword
- **Unified API**: Simple bilingual interface for seamless integration
- **Fallback Mechanisms**: Rule-based extraction when LLM is unavailable
- **Keyword Deduplication**: Automatic removal of duplicate keywords with confidence-based selection

### REST API (FastAPI)
- **Chinese Endpoint**: `POST /api/v1/keywords/chinese` - Extract keywords from Chinese text
- **English Endpoint**: `POST /api/v1/keywords/english` - Extract keywords from English text
- **Unified Endpoint**: `POST /api/v1/keywords` - Single interface for both languages
- **System Endpoints**: Language list, category list, health check
- **Auto Documentation**: Swagger UI (`/docs`) and ReDoc (`/redoc`)
- **Error Handling**: Proper HTTP status codes (400, 500) with descriptive messages
- **Production Ready**: Uvicorn server with easy deployment scripts

## 📦 Key Components

### Python SDK
- `keyword_recognition/models.py`: Data models for keywords and extraction results
- `keyword_recognition/chinese.py`: Chinese text processing and extraction (295 lines)
- `keyword_recognition/english.py`: English text processing and extraction (389 lines)
- `keyword_recognition/__init__.py`: Unified API interface (72 lines)
- `api.py`: FastAPI application (287 lines)

### Testing & Examples
- `tests/test_keyword_recognition.py`: 29 comprehensive unit tests (394 lines)
- `tests/test_english_abstract.py`: Move recognition tests (220 lines)
- `example_keyword.py`: Keyword extraction examples (205 lines)
- `api_example.py`: REST API usage examples (190 lines)
- `README_API.md`: Detailed API documentation (302 lines)

## 🔧 Technical Details

### LLM Integration
- Uses Zhipu AI GLM models for intelligent keyword extraction
- Implements proper error handling and fallback mechanisms
- Supports both LLM-enhanced and rule-based extraction modes
- Configurable model selection via environment variables
- **Fixed API message format** for Zhipu AI compatibility

### Data Models
- **Keyword**: Text, confidence, position, frequency, category
- **KeywordExtractionResult**: List of keywords with summary statistics
- **Language Enum**: Chinese and English support
- **Category Classification**: Technical, concept, domain, abbreviation, general, quantitative

### API Design
- RESTful architecture with proper HTTP methods
- Pydantic validation for requests and responses
- OpenAPI 3.0 specification auto-generation
- CORS support for web application integration
- Health check endpoint for monitoring

## 🧪 Testing

### Comprehensive Test Coverage
- **29 keyword recognition tests**: 100% pass rate
- **20 move recognition tests**: 100% pass rate  
- **Total**: 49 tests, all passing
- **Test Coverage**: Models, extraction logic, preprocessing, categorization, deduplication

### API Testing
All endpoints tested and verified:
- ✅ Health check endpoint
- ✅ Chinese keyword extraction
- ✅ English keyword extraction  
- ✅ Unified interface
- ✅ Languages endpoint
- ✅ Categories endpoint

## 📝 Examples

### Python SDK Usage
```python
from semantic_toolkit.keyword_recognition import extract_keywords, Language

# Chinese keyword extraction
result = extract_keywords(
    "深度学习算法在医疗诊断中的应用",
    language=Language.CHINESE,
    num_keywords=5
)

# English keyword extraction  
result = extract_keywords(
    "Deep learning algorithms for medical diagnosis",
    language=Language.ENGLISH,
    num_keywords=5
)

# Access categorized keywords
technical_keywords = result.get_keywords_by_category("technical")
top_keywords = result.get_top_keywords(10)
```

### REST API Usage
```bash
# Start API server
python -m semantic_toolkit.api

# Chinese keyword extraction
curl -X POST "http://localhost:8000/api/v1/keywords/chinese" \
  -H "Content-Type: application/json" \
  -d '{"text": "深度学习是机器学习的一个分支", "num_keywords": 5}'

# English keyword extraction
curl -X POST "http://localhost:8000/api/v1/keywords/english" \
  -H "Content-Type: application/json" \
  -d '{"text": "Deep learning is a subset of machine learning", "num_keywords": 5}'
```

## 🚀 Deployment

### Development
```bash
# Start API with auto-reload
uv run python -m semantic_toolkit.api

# Or use the provided script
./start_api.sh
```

### Production
```bash
# Using uvicorn (recommended)
uvicorn semantic_toolkit.api:app --host 0.0.0.0 --port 8000 --workers 4

# Using gunicorn for higher performance
gunicorn semantic_toolkit.api:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

## ✅ Test Plan
- [x] Unit tests for all data models
- [x] Chinese keyword extraction tests  
- [x] English keyword extraction tests
- [x] Unified interface tests
- [x] Text preprocessing tests
- [x] Keyword categorization tests
- [x] Deduplication tests
- [x] API endpoint tests
- [x] Error handling tests
- [x] Documentation tests
- [x] API message format fix for Zhipu AI

## 📊 Changes
- **23 files changed**
- **3,561 insertions(+)**
- **3 deletions(-)**
- **New features**: Keyword recognition, REST API
- **Documentation**: Complete API docs and examples
- **Testing**: Comprehensive test suite

## 🔗 Related Issues
Closes #[issue-number]

## 📖 Documentation
- **Main README**: Updated with API usage instructions
- **API Documentation**: `README_API.md` with detailed endpoint descriptions
- **Code Examples**: `example_keyword.py` and `api_example.py`
- **Interactive Docs**: Available at `/docs` and `/redoc` endpoints

## 🤝 Testing Instructions
```bash
# Install dependencies
uv sync

# Run unit tests
pytest tests/ -v

# Start API server
python -m semantic_toolkit.api

# Run API examples
python api_example.py

# Access documentation
# http://localhost:8000/docs
```

🤖 Generated with [Claude Code](https://claude.com/claude-code)
