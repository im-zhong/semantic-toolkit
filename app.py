import json
from pathlib import Path
from typing import Optional

import pandas as pd
import streamlit as st

from clc_classifier import CLCAutoClassifier, DEFAULT_JSON_PATH


st.set_page_config(page_title="自动分类工具", page_icon="📚", layout="wide")


def read_uploaded_file(uploaded_file) -> str:
    """
    读取上传文件内容。
    支持 txt / md / json / pdf。
    注意：普通文字版 PDF 可以解析；扫描图片版 PDF 需要 OCR，本函数无法直接识别。
    """
    if uploaded_file is None:
        return ""

    name = uploaded_file.name.lower()

    # 不使用 uploaded_file.read()
    # 因为 read() 可能被消费一次后指针到末尾，导致后续读取为空
    data = uploaded_file.getvalue()

    if name.endswith(".pdf"):
        try:
            from pypdf import PdfReader
            import io

            reader = PdfReader(io.BytesIO(data))
            pages_text = []

            for page in reader.pages:
                page_text = page.extract_text() or ""
                if page_text.strip():
                    pages_text.append(page_text)

            return "\n".join(pages_text).strip()

        except Exception as e:
            raise RuntimeError(f"PDF 解析失败：{e}")

    for enc in ("utf-8", "gb18030", "gbk"):
        try:
            return data.decode(enc).strip()
        except Exception:
            pass

    return data.decode("utf-8", errors="ignore").strip()


@st.cache_resource(show_spinner="正在加载中图分类法与本地召回索引...")
def get_classifier(json_path: str, model: str, top_k: int) -> CLCAutoClassifier:
    return CLCAutoClassifier(json_path=json_path, model=model or None, top_k=top_k)


def show_result(result: dict) -> None:
    inner = result.get("result", {})

    st.subheader("主分类结果")

    primary = inner.get("primary", {})
    alternatives = inner.get("alternatives", [])

    def normalize_class_id(class_id: str) -> str:
        """
        规范化分类号：
        [TP391] -> TP391
        S165+.27 -> S165+.27
        """
        return str(class_id or "").strip().replace("[", "").replace("]", "")

    def get_root_class(item: dict) -> str:
        """
        取中图分类号大类首字母：
        S165+.27 -> S
        TP391.4 -> T
        P48 -> P
        """
        cid = normalize_class_id(item.get("id", ""))
        return cid[0] if cid else ""

    all_items = [primary] + alternatives
    root_classes = {
        get_root_class(item)
        for item in all_items
        if get_root_class(item)
    }

    # 是否跨中图大类：严格按照分类号首字母判断
    is_cross_clc_root = len(root_classes) >= 2

    # 是否疑似技术交叉：读取模型返回的语义判断
    is_semantic_interdisciplinary = bool(inner.get("is_interdisciplinary", False))

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("是否跨中图大类", "是" if is_cross_clc_root else "否")

    with col2:
        st.metric("是否疑似技术交叉", "是" if is_semantic_interdisciplinary else "否")

    with col3:
        st.metric("涉及学科大类数", len(root_classes))

    with col4:
        st.metric("候选分类号数量", len(alternatives) + 1)

    if is_cross_clc_root:
        st.warning(
            "系统判断该文献跨越多个中图分类大类，建议结合主分类号和备选分类号人工确认。"
        )
    else:
        st.info("系统判断该文献学科归属相对集中，可优先采用主分类号。")

    st.success(f'{primary.get("id", "")}  {primary.get("name", "")}')
    st.write(f'**完整路径：** {primary.get("path", "")}')
    st.write(f'**置信度：** {primary.get("confidence", "")}')
    st.write(f'**原因：** {primary.get("reason", "")}')

    st.subheader("备选分类号")
    if alternatives:
        st.dataframe(
            pd.DataFrame(alternatives),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("暂无备选分类号。")

    st.subheader("关键词与选择建议")
    st.write("、".join(inner.get("keywords", [])) or "无")
    st.info(inner.get("user_selection_note", ""))

    with st.expander("查看本地召回 Top10 与完整 JSON"):
        st.write("本地召回 Top10")
        st.dataframe(
            pd.DataFrame(result.get("local_top_candidates", [])),
            use_container_width=True,
            hide_index=True,
        )
        st.write("完整 JSON")
        st.json(result, expanded=False)


def classify_panel(mode: str, title: str, help_text: str, domain_hint: Optional[str] = None) -> None:
    st.markdown(f"### {title}")
    st.caption(help_text)

    uploaded = st.file_uploader(
        "上传文献文件（支持 txt / md / json / pdf）",
        type=["txt", "md", "json", "pdf"],
        key=f"upload_{mode}",
    )

    file_text = ""

    if uploaded is not None:
        try:
            file_text = read_uploaded_file(uploaded)

            if file_text.strip():
                st.success(
                    f"文件已上传并解析成功：{uploaded.name}，共提取 {len(file_text)} 个字符。"
                )

                with st.expander("查看上传文件解析出的前 2000 字"):
                    st.write(file_text[:2000])
            else:
                st.warning(
                    "文件已上传，但没有解析出可用文字。"
                    "如果这是扫描版 PDF 或图片版 PDF，请复制摘要/正文粘贴到下方文本框。"
                )

        except Exception as e:
            st.error(str(e))

    text = st.text_area(
        "或直接粘贴文献标题、摘要、关键词、正文片段",
        value="",
        height=260,
        key=f"text_{mode}",
    )

    if st.button(f"开始{title}", type="primary", key=f"btn_{mode}"):

        # 关键修改：文本框为空时，自动使用上传文件解析出来的文本
        final_text = text.strip() or file_text.strip()

        if not final_text:
            st.warning(
                "请先上传可解析的文献文件，或直接粘贴文献标题、摘要、关键词、正文片段。"
            )
            return

        # 文本太长时截断，避免模型输入过长
        final_text = final_text[:12000]

        classifier = get_classifier(
            json_path=st.session_state["json_path"],
            model=st.session_state["model"],
            top_k=st.session_state["top_k"],
        )

        with st.spinner("正在进行本地候选召回与智谱模型重排..."):
            if mode == "zh":
                result = classifier.classify_chinese(final_text)
            elif mode == "en":
                result = classifier.classify_english(final_text)
            else:
                result = classifier.classify_domain(final_text, domain_hint=domain_hint or "")

        show_result(result)


st.title("📚 自动分类工具")
st.write("基于《中国图书馆分类法》科技类目，支持中文科技文献分类、英文科技文献分类、专业领域科技文献分类。")

with st.sidebar:
    st.header("系统配置")
    st.text_input("中图分类法 JSON 路径", value=DEFAULT_JSON_PATH, key="json_path")
    st.text_input("智谱模型名称", value="glm-4-flash", key="model")
    st.slider("本地候选召回数量", min_value=30, max_value=150, value=80, step=10, key="top_k")

    if st.button("检查分类库加载"):
        try:
            classifier = get_classifier(
                json_path=st.session_state["json_path"],
                model=st.session_state["model"],
                top_k=st.session_state["top_k"],
            )
            st.success(f"已加载科学技术类目：{classifier.store.count()} 个")
        except Exception as e:
            st.error(str(e))

tab1, tab2, tab3 = st.tabs(["中文科技文献分类", "英文科技文献分类", "专业领域科技文献分类"])

with tab1:
    classify_panel(
        mode="zh",
        title="中文科技文献分类",
        help_text="适合上传或粘贴中文论文题名、摘要、关键词、正文片段。",
    )

with tab2:
    classify_panel(
        mode="en",
        title="英文科技文献分类",
        help_text="适合上传或粘贴英文 paper title / abstract / keywords。系统会先抽取中文检索词再匹配中图类目。",
    )

with tab3:
    st.markdown("### 专业领域科技文献分类")
    domain_hint = st.text_input(
        "专业领域提示，可选",
        placeholder="例如：人工智能、医学影像、农业遥感、建筑工程、航空航天、环境治理",
    )
    classify_panel(
        mode="domain",
        title="专业领域科技文献分类",
        help_text="适合专业领域场景，可额外填写领域提示，提升交叉学科文献的候选召回效果。",
        domain_hint=domain_hint,
    )
