"""FastAPI application for keyword recognition API."""

from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from semantic_toolkit.keyword_recognition import (
    extract_chinese_keywords,
    extract_english_keywords,
    extract_keywords,
    Language,
)

# Create FastAPI app
app = FastAPI(
    title="Keyword Recognition API",
    description="API for extracting keywords from Chinese and English scientific literature",
    version="0.1.0",
)


# Request Models
class ChineseKeywordRequest(BaseModel):
    """Request model for Chinese keyword extraction."""

    text: str
    num_keywords: int = 10
    use_segmentation: bool = True

    class Config:
        json_schema_extra = {
            "example": {
                "text": "深度学习是机器学习的一个分支，它模仿人脑的神经网络结构。",
                "num_keywords": 5,
                "use_segmentation": True,
            }
        }


class EnglishKeywordRequest(BaseModel):
    """Request model for English keyword extraction."""

    text: str
    num_keywords: int = 10
    use_pos_tagging: bool = True

    class Config:
        json_schema_extra = {
            "example": {
                "text": "Deep learning is a subset of machine learning that mimics human brain structure.",
                "num_keywords": 5,
                "use_pos_tagging": True,
            }
        }


class UnifiedKeywordRequest(BaseModel):
    """Request model for unified keyword extraction."""

    text: str
    language: Language = Language.ENGLISH
    num_keywords: int = 10
    use_llm_fallback: bool = True

    class Config:
        json_schema_extra = {
            "example": {
                "text": "深度学习算法研究",
                "language": "chinese",
                "num_keywords": 5,
                "use_llm_fallback": True,
            }
        }


# Response Models
class KeywordResponse(BaseModel):
    """Response model for a single keyword."""

    text: str
    confidence: float
    position: int
    frequency: int
    category: str


class KeywordExtractionSummary(BaseModel):
    """Response model for extraction summary."""

    total_keywords: int
    average_confidence: float
    categories: dict
    top_keywords: List[dict]


class KeywordExtractionResponse(BaseModel):
    """Response model for keyword extraction."""

    language: str
    keywords: List[KeywordResponse]
    summary: KeywordExtractionSummary


# API Endpoints
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Keyword Recognition API",
        "version": "0.1.0",
        "description": "API for extracting keywords from scientific literature",
        "endpoints": {
            "chinese": "/api/v1/keywords/chinese",
            "english": "/api/v1/keywords/english",
            "unified": "/api/v1/keywords",
            "health": "/health",
            "docs": "/docs",
        },
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "keyword-recognition-api"}


@app.post(
    "/api/v1/keywords/chinese",
    response_model=KeywordExtractionResponse,
    tags=["Keywords"],
    summary="Extract keywords from Chinese text",
    description="Extract keywords from Chinese scientific literature using LLM with jieba segmentation fallback.",
)
async def extract_chinese_keywords_endpoint(request: ChineseKeywordRequest):
    """Extract keywords from Chinese text."""
    try:
        result = extract_chinese_keywords(
            text=request.text,
            num_keywords=request.num_keywords,
            use_segmentation=request.use_segmentation,
        )

        # Convert to response format
        keywords = [
            KeywordResponse(
                text=kw.text,
                confidence=kw.confidence,
                position=kw.position,
                frequency=kw.frequency,
                category=kw.category,
            )
            for kw in result.keywords
        ]

        return KeywordExtractionResponse(
            language=result.language.value,
            keywords=keywords,
            summary=KeywordExtractionSummary(**result.summary),
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post(
    "/api/v1/keywords/english",
    response_model=KeywordExtractionResponse,
    tags=["Keywords"],
    summary="Extract keywords from English text",
    description="Extract keywords from English scientific literature using LLM with NLTK POS tagging fallback.",
)
async def extract_english_keywords_endpoint(request: EnglishKeywordRequest):
    """Extract keywords from English text."""
    try:
        result = extract_english_keywords(
            text=request.text,
            num_keywords=request.num_keywords,
            use_pos_tagging=request.use_pos_tagging,
        )

        # Convert to response format
        keywords = [
            KeywordResponse(
                text=kw.text,
                confidence=kw.confidence,
                position=kw.position,
                frequency=kw.frequency,
                category=kw.category,
            )
            for kw in result.keywords
        ]

        return KeywordExtractionResponse(
            language=result.language.value,
            keywords=keywords,
            summary=KeywordExtractionSummary(**result.summary),
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post(
    "/api/v1/keywords",
    response_model=KeywordExtractionResponse,
    tags=["Keywords"],
    summary="Extract keywords from text (unified interface)",
    description="Extract keywords from text using unified interface that supports both Chinese and English.",
)
async def extract_keywords_unified_endpoint(request: UnifiedKeywordRequest):
    """Extract keywords from text using unified interface."""
    try:
        result = extract_keywords(
            text=request.text,
            language=request.language,
            num_keywords=request.num_keywords,
        )

        # Convert to response format
        keywords = [
            KeywordResponse(
                text=kw.text,
                confidence=kw.confidence,
                position=kw.position,
                frequency=kw.frequency,
                category=kw.category,
            )
            for kw in result.keywords
        ]

        return KeywordExtractionResponse(
            language=result.language.value,
            keywords=keywords,
            summary=KeywordExtractionSummary(**result.summary),
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get(
    "/api/v1/languages",
    tags=["System"],
    summary="Get supported languages",
    description="Get list of supported languages for keyword extraction.",
)
async def get_supported_languages():
    """Get supported languages."""
    return {
        "languages": [
            {"code": "chinese", "name": "Chinese", "native_name": "中文"},
            {"code": "english", "name": "English", "native_name": "English"},
        ]
    }


@app.get(
    "/api/v1/categories",
    tags=["System"],
    summary="Get keyword categories",
    description="Get list of possible keyword categories.",
)
async def get_keyword_categories():
    """Get keyword categories."""
    return {
        "categories": [
            {"code": "technical", "description": "Technical terms and algorithms"},
            {"code": "concept", "description": "Conceptual and theoretical terms"},
            {"code": "domain", "description": "Domain-specific terminology"},
            {"code": "abbreviation", "description": "Abbreviations and acronyms"},
            {"code": "general", "description": "General purpose terms"},
            {"code": "quantitative", "description": "Terms containing numbers or measurements"},
        ]
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
