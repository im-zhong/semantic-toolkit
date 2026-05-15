## 项目目录结构

```text
clc_zhipu_classifier_project/
│
├── clc_classifier.py              # 核心分类器模块
│   ├── Category                   # 分类数据类
│   ├── CategoryStore              # 分类法数据加载与管理
│   ├── TfidfCandidateRetriever    # 本地候选分类号召回器
│   ├── ZhipuClient                # 智谱 AI 客户端封装
│   └── CLCAutoClassifier          # 主分类服务
│
├── api.py                         # FastAPI 接口服务入口
│   ├── classify_text()            # 文本分类接口
│   ├── classify_file()            # 文件分类接口
│   ├── health_check()             # 健康检查接口
│   ├── get_modes()                # 分类模式查询接口
│   └── get_stats()                # 分类器统计信息接口
│
├── test_clc_classifier.py         # 分类器核心模块单元测试
├── test_api.py                    # API 接口单元测试
├── conftest.py                    # Pytest 测试配置和 fixtures
├── pytest.ini                     # Pytest 配置文件
│
├── requirements.txt               # 项目依赖
├── run_tests.bat                  # Windows 测试运行脚本
├── run_api.bat                    # Windows API 启动脚本
├── run_tests.sh                   # Linux / Mac 测试运行脚本
├── run_api.sh                     # Linux / Mac API 启动脚本
│
├── README.md                      # 项目说明文档
├── README_API.md                  # API 使用文档
├── PROJECT_STRUCTURE.md           # 项目结构说明
│
├── .env.example                   # 环境变量示例文件
├── .gitignore                     # Git 忽略配置
│
└── data/                          # 数据目录
    └── 完整版中国图书馆图书分类法.json
```

---

## 核心模块说明

### 1. clc_classifier.py

`clc_classifier.py` 是项目的核心分类模块，负责中图分类法数据加载、本地候选分类号召回、智谱 AI 调用和最终分类结果生成。

主要组成如下：

| 组件 | 说明 |
| --- | --- |
| Category | 分类数据结构，用于存储分类号、名称、路径等信息 |
| CategoryStore | 分类法数据加载与管理模块 |
| TfidfCandidateRetriever | 本地候选分类号召回器 |
| ZhipuClient | 智谱 AI API 调用封装 |
| CLCAutoClassifier | 主分类服务，提供统一分类入口 |

主要功能包括：

1. 加载中图分类法 JSON 数据
2. 提取科技类目分类信息
3. 根据输入文本召回候选分类号
4. 调用智谱 AI 模型生成分类结果
5. 支持中文、英文、专业领域三种分类模式
6. 支持交叉学科文献的候选分类号推荐

---

### 2. api.py

`api.py` 是 FastAPI 接口服务入口，负责将核心分类能力封装为 HTTP API。

主要接口包括：

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/` | 根路径，查看服务基本信息 |
| GET | `/health` | 健康检查接口 |
| POST | `/api/v1/classify` | 文本分类接口 |
| POST | `/api/v1/classify/file` | 文件分类接口 |
| GET | `/api/v1/modes` | 获取分类模式列表 |
| GET | `/api/v1/stats` | 获取分类器统计信息 |

当前 API 层固定使用后端配置：

```python
API_FIXED_MODEL = "glm-4-flash"
API_FIXED_TOP_K = 80
```

`model` 和 `top_k` 不作为接口参数暴露给用户，避免用户随意修改模型名称和候选召回数量。

---

## 测试模块说明

### 1. test_clc_classifier.py

用于测试分类器核心功能。

主要测试内容包括：

1. 工具函数是否正常
2. Category 数据类是否正常
3. CategoryStore 是否能正常加载分类法数据
4. 本地候选分类号召回是否正常
5. CLCAutoClassifier 是否能正常初始化
6. 中文分类逻辑是否正常
7. 英文分类逻辑是否正常
8. 专业领域分类逻辑是否正常
9. 交叉学科候选分类号逻辑是否正常

---

### 2. test_api.py

用于测试 FastAPI 接口功能。

主要测试内容包括：

1. 根路径接口是否正常
2. 健康检查接口是否正常
3. 分类模式接口是否正常
4. 分类器统计信息接口是否正常
5. 文本分类接口是否正常
6. 文件分类接口是否正常
7. 请求参数校验是否正常
8. 异常请求是否能返回合理错误信息

---

### 3. conftest.py

`conftest.py` 是 Pytest 测试配置文件。

主要作用：

1. 配置测试环境
2. 提供测试 fixtures
3. 提供模拟数据
4. 支持测试用例复用公共配置

---

## 配置文件说明

### 1. requirements.txt

项目依赖文件，用于安装项目运行和测试所需的 Python 第三方库。

安装命令：

```bash
pip install -r requirements.txt
```

---

### 2. pytest.ini

Pytest 配置文件，用于配置测试规则、测试路径和测试参数。

---

### 3. .env.example

环境变量示例文件。

使用时需要复制为 `.env`：

Windows：

```bash
copy .env.example .env
```

Linux / Mac：

```bash
cp .env.example .env
```

然后在 `.env` 中填写智谱 API Key：

```env
ZHIPUAI_API_KEY=你的智谱API_KEY
```

注意：`.env` 文件包含个人密钥，不要提交到 GitHub。

---

### 4. .gitignore

Git 忽略文件配置。

主要用于避免提交以下内容：

1. `.env`
2. `venv/`
3. `__pycache__/`
4. `.pytest_cache/`
5. 覆盖率报告目录
6. 本地临时文件

---

## 脚本文件说明

### 1. run_api.bat

Windows 系统下启动 API 服务的脚本。

运行方式：

```bash
run_api.bat
```

---

### 2. run_api.sh

Linux / Mac 系统下启动 API 服务的脚本。

运行方式：

```bash
bash run_api.sh
```

---

### 3. run_tests.bat

Windows 系统下运行测试的脚本。

运行方式：

```bash
run_tests.bat
```

---

### 4. run_tests.sh

Linux / Mac 系统下运行测试的脚本。

运行方式：

```bash
bash run_tests.sh
```

---

## 数据目录说明

### data/

`data/` 目录用于存放中图分类法 JSON 数据文件。

默认需要包含：

```text
完整版中国图书馆图书分类法.json
```

默认路径为：

```text
data/完整版中国图书馆图书分类法.json
```

如果数据文件名称或路径发生变化，需要同步修改代码中的默认数据路径配置。

---

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

---

### 2. 配置环境变量

复制 `.env.example` 为 `.env`，并填写智谱 API Key：

```env
ZHIPUAI_API_KEY=你的智谱API_KEY
```

---

### 3. 准备分类法数据

将以下文件放入 `data/` 目录：

```text
完整版中国图书馆图书分类法.json
```

---

### 4. 启动 API 服务

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

即可查看 FastAPI 自动生成的接口文档。

---

## 运行测试

运行全部测试：

```bash
pytest
```

或：

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

---

## 当前项目定位

当前项目定位为：

```text
中图分类法科技文献自动分类工具 API 服务
```

交付重点包括：

1. FastAPI 接口封装
2. 智谱 AI 模型调用
3. 中图分类法数据加载
4. 本地候选分类号召回
5. 中文科技文献分类
6. 英文科技文献分类
7. 专业领域科技文献分类
8. 交叉学科候选分类号推荐
9. API 单元测试
10. 后端固定配置管理

---

## 注意事项

1. `.env` 文件不要提交到 GitHub。
2. `venv/` 虚拟环境目录不要提交到 GitHub。
3. `__pycache__/` 不要提交到 GitHub。
4. `.pytest_cache/` 不要提交到 GitHub。
5. 中图分类法 JSON 文件需要放在 `data/` 目录下。
6. 当前项目只保留后端 API 服务。
7. FastAPI 自动生成的 `/docs` 页面不是自定义前端页面，可以保留。