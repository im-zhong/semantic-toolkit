from typing import Optional

from fastapi import HTTPException, Request

from auto_classifier.algorithms.clc_classifier import CLCAutoClassifier
from auto_classifier.config import API_FIXED_MODEL, API_FIXED_TOP_K, DEFAULT_JSON_PATH


_classifier: Optional[CLCAutoClassifier] = None


def get_classifier() -> CLCAutoClassifier:
    """获取或初始化分类器实例"""
    global _classifier

    if _classifier is None:
        _classifier = CLCAutoClassifier(
            json_path=str(DEFAULT_JSON_PATH),
            model=API_FIXED_MODEL,
            top_k=API_FIXED_TOP_K,
        )

    return _classifier


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