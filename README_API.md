# 中图分类法科技文献自动分类工具 API 文档

本文档用于说明中图分类法科技文献自动分类工具的 API 使用方式。

当前项目只提供后端 API 服务。  
调用方可以通过 HTTP 请求使用文本分类、文件分类、健康检查、分类模式查询和统计信息查询等功能。

---

## 一、安装依赖

在项目根目录执行：

```bash
pip install -r requirements.txt
```

如果使用虚拟环境，建议先激活虚拟环境后再安装依赖。

---

## 二、环境配置

项目需要配置智谱 API Key。

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

## 三、准备分类法数据

请将中图分类法 JSON 文件放到 `data/` 目录下。

默认文件路径为：

```text
data/完整版中国图书馆图书分类法.json
```

如果文件名或路径不同，需要同步修改代码中的默认数据路径配置。

---

## 四、启动 FastAPI 服务

### 方式一：直接运行

```bash
python api.py
```

### 方式二：使用 uvicorn

```bash
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

### 方式三：Windows 使用脚本启动

```bash
run_api.bat
```

### 方式四：Linux / Mac 使用脚本启动

```bash
bash run_api.sh
```

服务启动后，访问：

```text
http://localhost:8000/docs
```

即可打开 FastAPI 自动生成的接口文档。

也可以访问：

```text
http://localhost:8000/redoc
```

查看 ReDoc 接口文档。

---

## 五、基础地址

本地开发环境默认基础地址：

```text
http://localhost:8000
```

---

## 六、接口列表

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/` | 根路径，查看 API 基本信息 |
| GET | `/health` | 健康检查 |
| POST | `/api/v1/classify` | 文本分类 |
| POST | `/api/v1/classify/file` | 文件分类 |
| GET | `/api/v1/modes` | 获取分类模式 |
| GET | `/api/v1/stats` | 获取分类器统计信息 |

---

## 七、接口详情

## 1. 根路径接口

### 请求方式

```http
GET /
```

### 接口说明

用于查看 API 服务基本信息。

### 示例请求

```bash
curl http://localhost:8000/
```

### 示例响应

```json
{
  "name": "中图分类法科技文献自动分类工具 API",
  "version": "1.0.0",
  "description": "基于中图分类法和智谱 AI 的科技文献自动分类 API 服务"
}
```

---

## 2. 健康检查接口

### 请求方式

```http
GET /health
```

### 接口说明

用于检查 API 服务是否正常运行，以及分类器是否加载成功。

### 示例请求

```bash
curl http://localhost:8000/health
```

### 示例响应

```json
{
  "status": "healthy",
  "loaded_categories": 36201,
  "model": "glm-4-flash"
}
```

### 字段说明

| 字段名 | 说明 |
| --- | --- |
| status | 服务状态 |
| loaded_categories | 已加载的分类条目数量 |
| model | 当前后端固定使用的模型 |

---

## 3. 文本分类接口

### 请求方式

```http
POST /api/v1/classify
```

### 接口说明

根据输入的科技文献文本内容，自动推荐中图分类法分类号。

支持：

1. 中文科技文献分类
2. 英文科技文献分类
3. 专业领域科技文献分类
4. 交叉学科候选分类号推荐

---

### 请求头

```http
Content-Type: application/json
```

---

### 请求参数

| 参数名 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| text | string | 是 | 待分类的科技文献文本 |
| mode | string | 是 | 分类模式，支持 `zh`、`en`、`domain` |
| domain_hint | string | 否 | 专业领域提示，`domain` 模式下建议填写 |

---

### mode 取值说明

| mode | 说明 |
| --- | --- |
| zh | 中文科技文献分类 |
| en | 英文科技文献分类 |
| domain | 专业领域科技文献分类 |

---

### 中文分类请求示例

```json
{
  "text": "本文研究了深度学习在医学影像诊断中的应用，提出了一种基于卷积神经网络的肺部病灶识别方法。",
  "mode": "zh",
  "domain_hint": "医学影像"
}
```

---

### 英文分类请求示例

```json
{
  "text": "This paper proposes a convolutional neural network method for lung lesion recognition in medical imaging.",
  "mode": "en",
  "domain_hint": "medical imaging"
}
```

---

### 专业领域分类请求示例

```json
{
  "text": "本文研究了卷积神经网络在肺部 CT 图像识别中的应用。",
  "mode": "domain",
  "domain_hint": "医学影像"
}
```

---

### Windows cURL 示例

```bash
curl -X POST "http://localhost:8000/api/v1/classify" ^
  -H "Content-Type: application/json" ^
  -d "{\"text\":\"本文研究了深度学习在医学影像诊断中的应用。\",\"mode\":\"zh\",\"domain_hint\":\"医学影像\"}"
```

---

### Linux / Mac cURL 示例

```bash
curl -X POST "http://localhost:8000/api/v1/classify" \
  -H "Content-Type: application/json" \
  -d '{"text":"本文研究了深度学习在医学影像诊断中的应用。","mode":"zh","domain_hint":"医学影像"}'
```

---

### 示例响应

```json
{
  "tool": "中图分类法科技文献自动分类工具",
  "mode": "zh",
  "model": "glm-4-flash",
  "category_source": "data/完整版中国图书馆图书分类法.json",
  "loaded_scitech_categories": 36201,
  "candidate_count": 80,
  "result": {
    "language_detected": "中文",
    "is_interdisciplinary": true,
    "primary": {
      "code": "TP391",
      "name": "计算机应用"
    },
    "alternatives": [
      {
        "code": "R445",
        "name": "影像诊断学"
      }
    ],
    "keywords": [
      "深度学习",
      "医学影像",
      "卷积神经网络",
      "肺部病灶识别"
    ],
    "user_selection_note": "该文本同时涉及人工智能和医学影像，可优先选择计算机应用方向，医学影像方向作为备选。"
  },
  "local_top_candidates": []
}
```

---

## 4. 文件分类接口

### 请求方式

```http
POST /api/v1/classify/file
```

### 接口说明

上传文本类文件后，系统读取文件内容并进行自动分类。

---

### 请求类型

```http
multipart/form-data
```

---

### 请求参数

| 参数名 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| file | file | 是 | 待分类文件 |
| mode | string | 是 | 分类模式，支持 `zh`、`en`、`domain` |
| domain_hint | string | 否 | 专业领域提示 |
| encoding | string | 否 | 文件编码，默认 `utf-8` |

---

### Windows cURL 示例

```bash
curl -X POST "http://localhost:8000/api/v1/classify/file" ^
  -F "file=@document.txt" ^
  -F "mode=zh" ^
  -F "domain_hint=医学影像" ^
  -F "encoding=utf-8"
```

---

### Linux / Mac cURL 示例

```bash
curl -X POST "http://localhost:8000/api/v1/classify/file" \
  -F "file=@document.txt" \
  -F "mode=zh" \
  -F "domain_hint=医学影像" \
  -F "encoding=utf-8"
```

---

### 示例响应

```json
{
  "filename": "document.txt",
  "mode": "zh",
  "encoding": "utf-8",
  "classification": {
    "tool": "中图分类法科技文献自动分类工具",
    "mode": "zh",
    "model": "glm-4-flash",
    "result": {
      "language_detected": "中文",
      "is_interdisciplinary": false,
      "primary": {
        "code": "TP391",
        "name": "计算机应用"
      },
      "alternatives": [],
      "keywords": [
        "人工智能",
        "深度学习"
      ]
    }
  }
}
```

---

## 5. 分类模式查询接口

### 请求方式

```http
GET /api/v1/modes
```

### 接口说明

用于获取当前系统支持的分类模式。

### 示例请求

```bash
curl http://localhost:8000/api/v1/modes
```

### 示例响应

```json
{
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
      "description": "基于专业领域提示的深度分类，建议填写 domain_hint"
    }
  ]
}
```

---

## 6. 分类器统计信息接口

### 请求方式

```http
GET /api/v1/stats
```

### 接口说明

用于查看分类器当前加载状态和后端固定配置。

### 示例请求

```bash
curl http://localhost:8000/api/v1/stats
```

### 示例响应

```json
{
  "total_categories": 36201,
  "model": "glm-4-flash",
  "top_k": 80,
  "prompt_candidate_k": 35
}
```

---

## 八、后端固定配置说明

当前 API 服务固定使用以下配置：

```python
API_FIXED_MODEL = "glm-4-flash"
API_FIXED_TOP_K = 80
```

这两个参数不暴露给用户修改。

也就是说，请求体中不支持传入：

```json
{
  "model": "glm-4-plus",
  "top_k": 100
}
```

这样设计的原因是：

1. 保证接口行为稳定
2. 避免用户随意修改模型
3. 避免用户随意修改候选召回数量
4. 方便后续统一维护和部署
5. 符合后端 API 服务的交付要求

---

## 九、错误响应说明

### 1. 请求体字段校验失败

例如缺少 `text` 字段、`text` 为空，或者传入了接口不允许的字段。

状态码通常为：

```http
422 Unprocessable Entity
```

---

### 2. mode 参数不合法

如果传入了不支持的模式，例如：

```json
{
  "text": "测试文本",
  "mode": "abc"
}
```

可能返回：

```http
400 Bad Request
```

或者根据 Pydantic 校验规则返回：

```http
422 Unprocessable Entity
```

---

### 3. 分类器不可用

如果中图分类法数据文件不存在，或分类器初始化失败，可能返回：

```http
503 Service Unavailable
```

---

### 4. 服务端异常

如果调用智谱模型或分类处理过程中出现异常，可能返回：

```http
500 Internal Server Error
```

---

## 十、测试说明

运行全部测试：

```bash
pytest
```

详细输出：

```bash
pytest -v
```

运行 API 测试：

```bash
pytest test_api.py -v
```

运行分类器核心测试：

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

## 十一、Python 调用示例

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/classify",
    json={
        "text": "本文研究了深度学习在医学影像诊断中的应用",
        "mode": "zh",
        "domain_hint": "医学影像"
    }
)

result = response.json()
print(result)
```

健康检查示例：

```python
import requests

response = requests.get("http://localhost:8000/health")
print(response.json())
```

---

## 十二、调用流程建议

推荐调用流程：

1. 调用 `/health` 检查服务是否正常
2. 调用 `/api/v1/modes` 获取支持的分类模式
3. 调用 `/api/v1/classify` 进行文本分类
4. 如需上传文件，调用 `/api/v1/classify/file`
5. 如需查看分类器状态，调用 `/api/v1/stats`

---

## 十三、常见问题

### 1. API 启动失败

可能原因：

1. 依赖没有安装完整
2. 端口 8000 被占用
3. `.env` 没有正确配置
4. 中图分类法 JSON 文件路径不正确

可以先执行：

```bash
pip install -r requirements.txt
```

然后确认数据文件存在：

```text
data/完整版中国图书馆图书分类法.json
```

---

### 2. 分类器初始化失败

可能原因：

1. 中图分类法 JSON 文件不存在
2. JSON 文件格式不符合代码解析要求
3. 智谱 API Key 没有配置
4. 依赖包缺失

---

### 3. 文件上传失败

可能原因：

1. 上传文件不是文本格式
2. 文件编码不是 `utf-8`
3. 文件内容为空
4. 文件过大或读取失败

可以通过 `encoding` 参数指定编码。

---

## 十四、注意事项

1. `.env` 中必须配置 `ZHIPUAI_API_KEY`。
2. `.env` 不要提交到 GitHub。
3. 中图分类法 JSON 文件必须放在指定路径。
4. 当前项目只保留后端 API 服务。
5. `/docs` 和 `/redoc` 是 FastAPI 自动生成的接口文档，不是自定义前端页面。
6. `model` 和 `top_k` 由后端固定，不允许用户通过接口修改。