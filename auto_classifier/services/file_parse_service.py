from io import BytesIO
from pathlib import Path

from fastapi import HTTPException
from pypdf import PdfReader


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
                detail="PDF 未提取到文本内容，可能是扫描版 PDF，请先使用 OCR 或转换为文本文件。",
            )

        return text

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"PDF 解析失败：{str(e)}",
        )


def extract_text_from_upload_bytes(
    content: bytes,
    filename: str,
    content_type: str,
    encoding: str = "utf-8",
) -> str:
    """根据上传文件类型提取文本内容。"""

    if not content:
        raise HTTPException(status_code=422, detail="文件内容为空")

    suffix = Path(filename or "").suffix.lower()

    if suffix == ".pdf" or content_type == "application/pdf":
        text = extract_text_from_pdf_bytes(content)
    elif suffix in [".txt", ".md", ".json"] or suffix == "":
        try:
            text = content.decode(encoding)
        except UnicodeDecodeError:
            raise HTTPException(
                status_code=400,
                detail=f"文件解码失败，请检查编码设置（当前：{encoding}）",
            )
    else:
        raise HTTPException(
            status_code=400,
            detail="不支持的文件类型，目前仅支持 txt、md、json、pdf 文件",
        )

    text = text.strip()

    if not text:
        raise HTTPException(status_code=422, detail="文件文本内容为空")

    return text