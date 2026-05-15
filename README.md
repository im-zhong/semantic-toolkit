# semantic-toolkit

## 自动分类工具 API

本项目实现了一个基于 **中图分类法** 和 **智谱 AI 模型** 的科技文献自动分类工具。

系统可以根据输入的科技文献文本片段，自动推荐中图分类法中的科技类目分类号。对于存在交叉学科特征的文献，系统会给出主分类号和若干备选分类号，供用户进一步选择。

当前项目只提供后端 API 服务。  
前端页面或其他业务系统可以通过 HTTP API 调用本项目提供的分类能力。

---

## 核心功能

1. 支持中文科技文献分类
2. 支持英文科技文献分类
3. 支持专业领域科技文献分类
4. 支持交叉学科文献候选分类号推荐
5. 支持文本分类 API
6. 支持文件上传分类 API
7. 支持健康检查 API
8. 支持分类模式查询 API
9. 支持分类器统计信息 API
10. 使用环境变量管理智谱 API Key，避免密钥泄露
11. 后端固定模型名称和候选召回数量，不暴露给用户修改

---

## 技术栈

- Python
- FastAPI
- Uvicorn
- Pydantic
- 智谱 AI API
- Pytest

---

## 项目结构

```text
clc_zhipu_classifier_project/
│
├── api.py                         # FastAPI 接口服务入口
├── clc_classifier.py              # 中图分类法自动分类核心逻辑
├── conftest.py                    # Pytest 测试配置
│
├── test_api.py                    # API 接口测试
├── test_clc_classifier.py         # 分类器核心逻辑测试
│
├── requirements.txt               # 项目依赖
├── pytest.ini                     # Pytest 配置
│
├── run_api.bat                    # Windows 启动 API 脚本
├── run_api.sh                     # Linux / Mac 启动 API 脚本
├── run_tests.bat                  # Windows 运行测试脚本
├── run_tests.sh                   # Linux / Mac 运行测试脚本
│
├── README.md                      # 项目说明文档
├── README_API.md                  # API 使用文档
├── PROJECT_STRUCTURE.md           # 项目结构说明
│
├── .env.example                   # 环境变量示例
├── .gitignore                     # Git 忽略配置
│
└── data/
    └── 完整版中国图书馆图书分类法.json
```

---

## 运行步骤

### 1. 准备数据文件

将中图分类法 JSON 文件放到 `data/` 目录下。

默认文件路径为：

```text
data/完整版中国图书馆图书分类法.json
```

注意文件名需要和代码中的默认路径保持一致。

---

### 2. 安装依赖

在项目根目录执行：

```bash
pip install -r requirements.txt
```

如果使用虚拟环境，建议先激活虚拟环境后再安装依赖。

Windows 示例：

```bash
venv\Scripts\activate
pip install -r requirements.txt
```

---

### 3. 配置智谱 API Key

复制 `.env.example` 为 `.env`。

Windows：

```bash
copy .env.example .env
```

Linux / Mac：

```bash
cp .env.example .env
```

然后在 `.env` 中填写：

```env
ZHIPUAI_API_KEY=你的智谱API_KEY
```

注意：`.env` 文件包含个人密钥，不要提交到 GitHub。

---

### 4. 启动 FastAPI 服务

方式一：直接运行：

```bash
python api.py
```

方式二：使用 uvicorn 启动：

```bash
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

方式三：Windows 使用脚本启动：

```bash
run_api.bat
```

方式四：Linux / Mac 使用脚本启动：

```bash
bash run_api.sh
```

---

### 5. 访问接口文档

服务启动成功后，浏览器访问：

```text
http://localhost:8000/docs
```

即可查看 FastAPI 自动生成的接口文档，并可以直接在页面中测试接口。

---

## 主要接口

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/` | 根路径，查看 API 基本信息 |
| GET | `/health` | 健康检查 |
| POST | `/api/v1/classify` | 文本分类 |
| POST | `/api/v1/classify/file` | 文件分类 |
| GET | `/api/v1/modes` | 获取分类模式 |
| GET | `/api/v1/stats` | 获取分类器统计信息 |

---

## 文本分类请求示例

请求接口：

```http
POST /api/v1/classify
```

请求体示例：

```json
{
  "text": "本文研究了深度学习在医学影像诊断中的应用，提出了一种基于卷积神经网络的肺部病灶识别方法。",
  "mode": "zh",
  "domain_hint": "医学影像"
}
```

参数说明：

| 参数名 | 是否必填 | 说明 |
| --- | --- | --- |
| text | 是 | 待分类的科技文献文本 |
| mode | 是 | 分类模式，支持 `zh`、`en`、`domain` |
| domain_hint | 否 | 专业领域提示，`domain` 模式下建议填写 |

---

## 文件分类请求示例

请求接口：

```http
POST /api/v1/classify/file
```

请求类型：

```text
multipart/form-data
```

参数说明：

| 参数名 | 是否必填 | 说明 |
| --- | --- | --- |
| file | 是 | 待分类文件 |
| mode | 是 | 分类模式，支持 `zh`、`en`、`domain` |
| domain_hint | 否 | 专业领域提示 |
| encoding | 否 | 文件编码，默认 `utf-8` |

---

## 分类模式说明

| mode | 说明 |
| --- | --- |
| zh | 中文科技文献分类 |
| en | 英文科技文献分类 |
| domain | 专业领域科技文献分类 |

当使用 `domain` 模式时，建议填写 `domain_hint`。

示例：

```json
{
  "text": "本文研究了卷积神经网络在肺部 CT 图像识别中的应用。",
  "mode": "domain",
  "domain_hint": "医学影像"
}
```

---

## 后端固定配置说明

当前 API 层固定使用以下配置：

```python
API_FIXED_MODEL = "glm-4-flash"
API_FIXED_TOP_K = 80
```

也就是说：

1. 用户不能通过接口修改模型名称
2. 用户不能通过接口修改候选召回数量
3. 模型和召回数量由后端统一控制
4. API 请求参数更加简洁稳定

接口中不暴露 `model` 和 `top_k` 参数。

---

## 返回结果说明

分类接口通常会返回以下内容：

| 字段名 | 说明 |
| --- | --- |
| tool | 工具名称 |
| mode | 当前分类模式 |
| model | 后端实际使用的模型 |
| category_source | 分类法数据来源 |
| loaded_scitech_categories | 已加载的分类条目数量 |
| candidate_count | 候选分类数量 |
| result | 智谱模型返回的分类结果 |
| local_top_candidates | 本地召回的候选分类结果 |

其中 `result` 中通常包含：

| 字段名 | 说明 |
| --- | --- |
| language_detected | 检测到的文本语言 |
| is_interdisciplinary | 是否为交叉学科 |
| primary | 主分类号 |
| alternatives | 备选分类号 |
| keywords | 关键词 |
| user_selection_note | 分类选择说明 |

---

## 错误处理说明

常见状态码如下：

| 状态码 | 说明 |
| --- | --- |
| 400 | 请求参数内容不合法 |
| 422 | 请求体字段校验失败，例如缺少字段、字段为空、传入不允许的字段 |
| 500 | 服务端处理异常 |
| 503 | 分类器初始化失败或服务不可用 |

---

## 运行测试

运行全部测试：

```bash
pytest
```

或者：

```bash
pytest -v
```

Windows 使用脚本运行：

```bash
run_tests.bat
```

Linux / Mac 使用脚本运行：

```bash
bash run_tests.sh
```

运行 API 测试：

```bash
pytest test_api.py -v
```

运行分类器测试：

```bash
pytest test_clc_classifier.py -v
```

生成测试覆盖率报告：

```bash
pytest --cov=. --cov-report=html
```

生成后可以打开：

```text
htmlcov/index.html
```

查看测试覆盖率报告。

---

## 注意事项

1. `.env` 文件不要提交到 GitHub。
2. `venv/` 虚拟环境目录不要提交到 GitHub。
3. `__pycache__/` 不要提交到 GitHub。
4. `.pytest_cache/` 不要提交到 GitHub。
5. 如果误提交过 `.env`，建议立即重置智谱 API Key。
6. 中图分类法 JSON 文件需要放在 `data/` 目录下。
7. 当前项目只保留后端 API 服务。
8. FastAPI 自动生成的 `/docs` 页面不是自定义前端页面，可以保留。

---

## 快速验证流程

1. 安装依赖：

```bash
pip install -r requirements.txt
```

2. 配置 `.env`：

```env
ZHIPUAI_API_KEY=你的智谱API_KEY
```

3. 启动服务：

```bash
python api.py
```

4. 打开接口文档：

```text
http://localhost:8000/docs
```

5. 测试健康检查：

```text
http://localhost:8000/health
```

6. 运行单元测试：

```bash
pytest -v
```

如果 API 能正常启动，`/health` 能正常返回，测试能通过，说明项目后端 API 基本可用。

---

## PR 说明建议

本次 PR 可以概括为：

```text
完成中图分类自动分类工具 API 封装
```

PR 描述可以写：

```text
1. 移除自定义页面和命令行入口，仅保留后端 API 服务
2. 新增文本分类接口 /api/v1/classify
3. 新增文件分类接口 /api/v1/classify/file
4. 新增健康检查接口 /health
5. 新增分类模式查询接口 /api/v1/modes
6. 新增分类器统计信息接口 /api/v1/stats
7. 固定后端模型名称和候选召回数量，不暴露给用户修改
8. 补充 API 单元测试和运行脚本
```