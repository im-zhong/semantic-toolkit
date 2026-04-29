"""FastAPI接口封装 - 中图分类法科技文献自动分类工具"""

from typing import Optional

from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from io import BytesIO
from pathlib import Path
from pypdf import PdfReader
from clc_classifier import CLCAutoClassifier, DEFAULT_JSON_PATH

app = FastAPI(
    title="中图分类法科技文献自动分类API",
    description="基于智谱AI和中图分类法的科技文献自动分类服务",
    version="1.0.0"
)

# API 层固定配置：不暴露给用户请求修改
API_FIXED_MODEL = "glm-4-flash"
API_FIXED_TOP_K = 80

# 全局分类器实例
_classifier: Optional[CLCAutoClassifier] = None

def extract_text_from_pdf_bytes(file_bytes: bytes) -> str:
    """
    从 PDF 文件字节中提取文本。
    注意：只支持可复制文本的 PDF，不支持纯扫描图片 PDF。
    """
    try:
        reader = PdfReader(BytesIO(file_bytes))
        pages_text = []

        for page in reader.pages:
            page_text = page.extract_text() or ""
            if page_text.strip():
                pages_text.append(page_text.strip())

        text = "\n\n".join(pages_text).strip()

        if not text:
            raise HTTPException(
                status_code=400,
                detail="PDF 未提取到文本内容，可能是扫描版 PDF，请先使用 OCR 或转换为文本文件。"
            )

        return text

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"PDF 解析失败：{str(e)}"
        )

def get_classifier() -> CLCAutoClassifier:
    """获取或初始化分类器实例"""
    global _classifier
    if _classifier is None:
        _classifier = CLCAutoClassifier(
            json_path=DEFAULT_JSON_PATH,
            model=API_FIXED_MODEL,
            top_k=API_FIXED_TOP_K,
        )
    return _classifier


class ClassifyRequest(BaseModel):
    """分类请求模型"""
    text: str = Field(..., description="待分类的文本内容", min_length=1)
    mode: str = Field(..., description="分类模式：zh(中文)、en(英文)、domain(专业领域)")
    domain_hint: Optional[str] = Field(None, description="专业领域提示，domain模式推荐填写")

    class Config:
        extra = "forbid"


class ClassifyResponse(BaseModel):
    """分类响应模型"""
    tool: str
    mode: str
    model: str
    category_source: str
    loaded_scitech_categories: int
    candidate_count: int
    result: dict
    local_top_candidates: list


@app.get("/")
async def root():
    """根路径，返回API信息"""
    return {
        "name": "中图分类法科技文献自动分类API",
        "version": "1.0.0",
        "endpoints": {
            "classify": "/api/v1/classify - 文本分类",
            "classify_file": "/api/v1/classify/file - 文件分类",
            "health": "/health - 健康检查"
        }
    }


@app.get("/health")
async def health_check():
    """健康检查接口"""
    try:
        classifier = get_classifier()
        return {
            "status": "healthy",
            "loaded_categories": classifier.store.count(),
            "model": classifier.llm.model
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"服务不可用: {str(e)}")


@app.post("/api/v1/classify", response_model=ClassifyResponse)
async def classify_text(request: ClassifyRequest):
    """
    文本分类接口

    - **text**: 待分类的文本内容
    - **mode**: 分类模式（zh/en/domain）
    - **domain_hint**: 专业领域提示（可选，domain模式推荐）
    """
    try:
        classifier = get_classifier()

        # 验证mode参数
        if request.mode not in ["zh", "en", "domain"]:
            raise HTTPException(
                status_code=400,
                detail="mode参数必须是 zh、en 或 domain 之一"
            )

        # 根据模式调用相应的分类方法
        if request.mode == "zh":
            result = classifier.classify_chinese(request.text)
        elif request.mode == "en":
            result = classifier.classify_english(request.text)
        else:  # domain
            result = classifier.classify_domain(
                request.text,
                domain_hint=request.domain_hint or ""
            )

        return result

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分类失败: {str(e)}")

async def reject_unsupported_file_form_params(request: Request):
    """拒绝用户通过文件接口传入后端固定参数。"""
    form = await request.form()
    forbidden = {"model", "top_k"} & set(form.keys())
    if forbidden:
        raise HTTPException(
            status_code=422,
            detail=(
                f"不支持的参数：{', '.join(sorted(forbidden))}。"
                "model 和 top_k 由后端固定配置，不能通过接口修改。"
            ),
        )

@app.post("/api/v1/classify/file", response_model=ClassifyResponse)
async def classify_file(
    file: UploadFile = File(..., description="待分类的文件，支持 txt/md/json/pdf 等格式"),
    mode: str = Form(..., description="分类模式：zh(中文)、en(英文)、domain(专业领域)"),
    domain_hint: Optional[str] = Form(None, description="专业领域提示"),
    encoding: str = Form("utf-8", description="文本文件编码，默认 utf-8"),
    _: None = Depends(reject_unsupported_file_form_params),
):
    """
    文件分类接口

    - **file**: 上传的文件，支持 txt/md/json/pdf
    - **mode**: 分类模式，支持 zh、en、domain
    - **domain_hint**: 专业领域提示，可选
    - **encoding**: 文本文件编码，默认 utf-8
    """
    try:
        # 验证 mode 参数
        if mode not in ["zh", "en", "domain"]:
            raise HTTPException(
                status_code=400,
                detail="mode 参数必须是 zh、en 或 domain 之一"
            )

        # 读取文件内容
        content = await file.read()

        if not content:
            raise HTTPException(
                status_code=422,
                detail="文件内容为空"
            )

        filename = file.filename or ""
        suffix = Path(filename).suffix.lower()
        content_type = file.content_type or ""

        # 根据文件类型提取文本
        if suffix == ".pdf" or content_type == "application/pdf":
            text = extract_text_from_pdf_bytes(content)
        elif suffix in [".txt", ".md", ".json"] or suffix == "":
            try:
                text = content.decode(encoding)
            except UnicodeDecodeError:
                raise HTTPException(
                    status_code=400,
                    detail=f"文件解码失败，请检查编码设置（当前：{encoding}）"
                )
        else:
            raise HTTPException(
                status_code=400,
                detail="不支持的文件类型，目前仅支持 txt、md、json、pdf 文件"
            )

        text = text.strip()

        if not text:
            raise HTTPException(
                status_code=422,
                detail="文件文本内容为空"
            )

        classifier = get_classifier()

        # 根据模式调用相应的分类方法
        if mode == "zh":
            result = classifier.classify_chinese(text)
        elif mode == "en":
            result = classifier.classify_english(text)
        else:
            result = classifier.classify_domain(
                text,
                domain_hint=domain_hint or ""
            )

        return result

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"分类失败: {str(e)}"
        )


@app.get("/api/v1/modes")
async def get_modes():
    """获取支持的分类模式列表"""
    return {
        "modes": [
            {
                "code": "zh",
                "name": "中文科技文献分类",
                "description": "用于中文科技文献的自动分类"
            },
            {
                "code": "en",
                "name": "英文科技文献分类",
                "description": "用于英文科技文献的自动分类"
            },
            {
                "code": "domain",
                "name": "专业领域科技文献分类",
                "description": "基于专业领域提示的深度分类，建议填写domain_hint"
            }
        ]
    }


@app.get("/api/v1/stats")
async def get_stats():
    """获取分类器统计信息"""
    try:
        classifier = get_classifier()
        return {
            "total_categories": classifier.store.count(),
            "model": classifier.llm.model,
            "top_k": classifier.top_k,
            "prompt_candidate_k": classifier.prompt_candidate_k
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"服务不可用: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
