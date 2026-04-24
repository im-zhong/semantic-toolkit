# semantic-toolkit

TEST 2

---

# 自动分类工具

## 运行步骤

1. 把 `完整版本中国图书馆图书分类法.json` 放到 `data/` 目录。
2. 安装依赖：`pip install -r requirements.txt`
3. 配置智谱 API Key：复制 `.env.example` 为 `.env`，填写 `ZHIPUAI_API_KEY`。
4. 启动 Web 界面：`streamlit run app.py`
5. 或使用 CLI：
   - 中文：`python cli.py --mode zh --text "这里放中文摘要"`
   - 英文：`python cli.py --mode en --text "This paper proposes..."`
   - 专业领域：`python cli.py --mode domain --domain-hint "医学影像" --text "这里放摘要"`