from typing import Optional

from fastapi import APIRouter, Body, Depends, File, Form, HTTPException, UploadFile

from auto_classifier.dependencies import (
    get_classifier,
    reject_unsupported_file_form_params,
)
from auto_classifier.schemas.classify import ClassifyRequest, ClassifyResponse
from auto_classifier.services.file_parse_service import extract_text_from_upload_bytes

router = APIRouter(
    prefix="/api/v1",
    tags=["自动分类工具"],
)


@router.post(
    "/classify",
    response_model=ClassifyResponse,
    summary="文本分类接口",
    description="""
根据输入的科技文献文本，自动推荐中图分类号。

### 请求字段说明

| 字段名 | 是否必填 | 填写要求 | 示例 |
|---|---|---|---|
| text | 必填 | 待分类的科技文献文本，不能为空，建议填写标题、摘要或正文片段 | 本文提出一种基于深度学习的遥感图像目标检测方法 |
| mode | 必填 | 分类模式，只能填写 zh、en、domain | zh |
| domain_hint | 选填 | 专业领域提示。mode=domain 时建议填写，mode=zh/en 时可不填 | 人工智能/医学影像 |

### mode 参数说明

- zh：中文科技文献分类
- en：英文科技文献分类
- domain：专业领域科技文献分类
""",
    response_description="分类结果",
)
async def classify_text(
    request: ClassifyRequest = Body(
        ...,
        description="文本分类请求体",
        openapi_examples={
            "中文科技文献分类": {
                "summary": "中文科技文献分类示例",
                "description": "mode=zh，适用于中文科技文献。",
                "value": {
                    "text": "本文提出一种基于深度学习的遥感图像目标检测方法，可用于复杂场景下的目标识别与分类。",
                    "mode": "zh",
                    "domain_hint": ""
                },
            },
            "英文科技文献分类": {
                "summary": "英文科技文献分类示例",
                "description": "mode=en，适用于英文科技文献。",
                "value": {
                    "text": "This paper proposes a deep learning method for remote sensing image object detection.",
                    "mode": "en",
                    "domain_hint": ""
                },
            },
            "专业领域科技文献分类": {
                "summary": "专业领域分类示例",
                "description": "mode=domain，建议填写 domain_hint。",
                "value": {
                    "text": "本文围绕医学影像智能诊断任务，构建了一种多模态深度学习分类模型。",
                    "mode": "domain",
                    "domain_hint": "医学影像/人工智能"
                },
            },
        },
    )
):
    """文本分类接口"""
    try:
        classifier = get_classifier()

        if request.mode not in ["zh", "en", "domain"]:
            raise HTTPException(
                status_code=400,
                detail="mode参数必须是 zh、en 或 domain 之一",
            )

        if request.mode == "zh":
            result = classifier.classify_chinese(request.text)
        elif request.mode == "en":
            result = classifier.classify_english(request.text)
        else:
            result = classifier.classify_domain(
                request.text,
                domain_hint=request.domain_hint or "",
            )

        return result

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分类失败: {str(e)}")


@router.post("/classify/file", response_model=ClassifyResponse)
async def classify_file(
    file: UploadFile = File(..., description="待分类的文件，支持 txt/md/json/pdf 等格式"),
    mode: str = Form(..., description="分类模式：zh(中文)、en(英文)、domain(专业领域)"),
    domain_hint: Optional[str] = Form(None, description="专业领域提示"),
    encoding: str = Form("utf-8", description="文本文件编码，默认 utf-8"),
    _: None = Depends(reject_unsupported_file_form_params),
):
    """文件分类接口"""
    try:
        if mode not in ["zh", "en", "domain"]:
            raise HTTPException(
                status_code=400,
                detail="mode 参数必须是 zh、en 或 domain 之一",
            )

        content = await file.read()

        text = extract_text_from_upload_bytes(
            content=content,
            filename=file.filename or "",
            content_type=file.content_type or "",
            encoding=encoding,
        )

        classifier = get_classifier()

        if mode == "zh":
            result = classifier.classify_chinese(text)
        elif mode == "en":
            result = classifier.classify_english(text)
        else:
            result = classifier.classify_domain(
                text,
                domain_hint=domain_hint or "",
            )

        return result

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分类失败: {str(e)}")


@router.get("/modes")
async def get_modes():
    """获取支持的分类模式列表"""
    return {
        "modes": [
            {
                "code": "zh",
                "name": "中文科技文献分类",
                "description": "用于中文科技文献的自动分类",
            },
            {
                "code": "en",
                "name": "英文科技文献分类",
                "description": "用于英文科技文献的自动分类",
            },
            {
                "code": "domain",
                "name": "专业领域科技文献分类",
                "description": "基于专业领域提示的深度分类，建议填写domain_hint",
            },
        ]
    }


@router.get("/stats")
async def get_stats():
    """获取分类器统计信息"""
    try:
        classifier = get_classifier()
        return {
            "total_categories": classifier.store.count(),
            "model": classifier.llm.model,
            "top_k": classifier.top_k,
            "prompt_candidate_k": classifier.prompt_candidate_k,
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"服务不可用: {str(e)}")