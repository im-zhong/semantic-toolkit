from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ClassifyRequest(BaseModel):
    """文本分类请求模型"""

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "text": "本文提出一种基于深度学习的遥感图像目标检测方法，可用于复杂场景下的目标识别与分类。",
                    "mode": "zh",
                    "domain_hint": ""
                },
                {
                    "text": "This paper proposes a deep learning method for remote sensing image object detection.",
                    "mode": "en",
                    "domain_hint": ""
                },
                {
                    "text": "本文围绕医学影像智能诊断任务，构建了一种多模态深度学习分类模型。",
                    "mode": "domain",
                    "domain_hint": "医学影像/人工智能"
                }
            ]
        },
    )

    text: str = Field(
        ...,
        title="待分类文本（必填）",
        description="必填。需要分类的科技文献文本内容，不能为空。建议填写标题、摘要或正文片段。",
        min_length=1,
        examples=[
            "本文提出一种基于深度学习的遥感图像目标检测方法，可用于复杂场景下的目标识别与分类。"
        ],
    )

    mode: Literal["zh", "en", "domain"] = Field(
        ...,
        title="分类模式（必填）",
        description=(
            "必填。分类模式只能填写以下三种之一："
            "zh=中文科技文献分类；"
            "en=英文科技文献分类；"
            "domain=专业领域科技文献分类。"
        ),
        examples=["zh"],
    )

    domain_hint: Optional[str] = Field(
        None,
        title="专业领域提示（选填）",
        description=(
            "选填。仅当 mode=domain 时建议填写，用于提示专业领域；"
            "当 mode=zh 或 mode=en 时可以不填或传空字符串。"
        ),
        examples=["人工智能/医学影像/遥感科学"],
    )

    @field_validator("text")
    @classmethod
    def validate_text_not_blank(cls, value: str) -> str:
        """校验文本不能为空或纯空格"""
        if not value or not value.strip():
            raise ValueError("text 为必填项，不能为空字符串或纯空格")
        return value.strip()

    @field_validator("domain_hint")
    @classmethod
    def clean_domain_hint(cls, value: Optional[str]) -> Optional[str]:
        """去除专业领域提示前后的空格"""
        if value is None:
            return value
        return value.strip()


class ClassifyResponse(BaseModel):
    """分类响应模型"""

    tool: str = Field(..., description="工具名称")
    mode: str = Field(..., description="本次使用的分类模式")
    model: str = Field(..., description="后端固定使用的智谱模型名称")
    category_source: str = Field(..., description="分类号数据来源")
    loaded_scitech_categories: int = Field(..., description="已加载的科技类中图分类号数量")
    candidate_count: int = Field(..., description="候选分类号数量")
    result: dict[str, Any] = Field(..., description="模型返回的分类结果")
    local_top_candidates: list = Field(..., description="本地召回的候选分类号列表")