from fastapi import APIRouter, HTTPException

from auto_classifier.dependencies import get_classifier

router = APIRouter(
    tags=["服务状态"],
)


@router.get("/")
async def root():
    """根路径，返回API信息"""
    return {
        "name": "中图分类法科技文献自动分类API",
        "version": "1.0.0",
        "endpoints": {
            "classify": "/api/v1/classify - 文本分类",
            "classify_file": "/api/v1/classify/file - 文件分类",
            "modes": "/api/v1/modes - 分类模式列表",
            "stats": "/api/v1/stats - 分类器统计信息",
            "health": "/health - 健康检查",
        },
    }


@router.get("/health")
async def health_check():
    """健康检查接口"""
    try:
        classifier = get_classifier()
        return {
            "status": "healthy",
            "loaded_categories": classifier.store.count(),
            "model": classifier.llm.model,
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"服务不可用: {str(e)}")