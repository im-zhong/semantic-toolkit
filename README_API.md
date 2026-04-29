# Keyword Recognition API

FastAPI应用，提供中英文科技文献关键词识别的REST API接口。

## 🚀 快速开始

### 安装依赖

```bash
uv sync
```

### 启动API服务

```bash
# 使用uv启动
uv run python -m semantic_toolkit.api

# 或直接启动
python -m semantic_toolkit.api
```

服务将在 `http://localhost:8000` 启动。

### 访问API文档

启动服务后，可以通过以下地址访问API文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📡 API端点

### 基础端点

#### `GET /`
获取API基本信息和可用端点列表。

#### `GET /health`
健康检查端点，用于监控服务状态。

#### `GET /api/v1/languages`
获取支持的语言列表。

#### `GET /api/v1/categories`
获取关键词分类列表。

### 关键词提取端点

#### `POST /api/v1/keywords/chinese`
从中文文本中提取关键词。

**请求体:**
```json
{
  "text": "深度学习是机器学习的一个分支",
  "num_keywords": 5,
  "use_segmentation": true
}
```

**参数说明:**
- `text` (string, 必需): 要分析的中文文本
- `num_keywords` (integer, 可选): 要提取的关键词数量，默认10
- `use_segmentation` (boolean, 可选): 是否使用jieba分词，默认true

**响应:**
```json
{
  "language": "chinese",
  "keywords": [
    {
      "text": "深度学习",
      "confidence": 0.95,
      "position": 0,
      "frequency": 1,
      "category": "technical"
    }
  ],
  "summary": {
    "total_keywords": 5,
    "average_confidence": 0.84,
    "categories": {"technical": 3, "general": 2},
    "top_keywords": [...]
  }
}
```

#### `POST /api/v1/keywords/english`
从英文文本中提取关键词。

**请求体:**
```json
{
  "text": "Deep learning is a subset of machine learning",
  "num_keywords": 5,
  "use_pos_tagging": true
}
```

**参数说明:**
- `text` (string, 必需): 要分析的英文文本
- `num_keywords` (integer, 可选): 要提取的关键词数量，默认10
- `use_pos_tagging` (boolean, 可选): 是否使用NLTK词性标注，默认true

**响应格式与中文端点相同。**

#### `POST /api/v1/keywords`
统一接口，支持中英文关键词提取。

**请求体:**
```json
{
  "text": "机器学习算法研究",
  "language": "chinese",
  "num_keywords": 5,
  "use_llm_fallback": true
}
```

**参数说明:**
- `text` (string, 必需): 要分析的文本
- `language` (string, 可选): 语言类型（"chinese"或"english"），默认"english"
- `num_keywords` (integer, 可选): 要提取的关键词数量，默认10
- `use_llm_fallback` (boolean, 可选): 是否使用LLM回退机制，默认true

## 💡 使用示例

### 使用curl

```bash
# 中文关键词提取
curl -X POST "http://localhost:8000/api/v1/keywords/chinese" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "深度学习是机器学习的一个分支",
    "num_keywords": 5
  }'

# 英文关键词提取
curl -X POST "http://localhost:8000/api/v1/keywords/english" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Deep learning is a subset of machine learning",
    "num_keywords": 5
  }'
```

### 使用Python requests

```python
import requests

# 中文关键词提取
response = requests.post(
    "http://localhost:8000/api/v1/keywords/chinese",
    json={
        "text": "深度学习是机器学习的一个分支",
        "num_keywords": 5
    }
)
result = response.json()
print([kw['text'] for kw in result['keywords']])

# 英文关键词提取
response = requests.post(
    "http://localhost:8000/api/v1/keywords/english",
    json={
        "text": "Deep learning is a subset of machine learning",
        "num_keywords": 5
    }
)
result = response.json()
print([kw['text'] for kw in result['keywords']])
```

### 运行完整示例

```bash
# 确保API服务已启动，然后运行示例
python api_example.py
```

## 🔧 配置

### 环境变量

在 `.env` 文件中配置：

```bash
# 智谱AI API密钥（必需）
ZHIPU_API_KEY=your-api-key-here

# 使用的模型（可选，默认glm-4）
ZHIPU_MODEL=glm-4
```

### 服务配置

可以修改 `src/semantic_toolkit/api.py` 中的启动参数：

```python
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",  # 监听地址
        port=8000,           # 监听端口
        reload=True           # 开发模式（自动重载）
    )
```

## 📊 关键词分类

API会自动将关键词分类为以下类型：

- **technical**: 技术术语和算法
- **concept**: 概念和理论术语
- **domain**: 领域相关术语
- **abbreviation**: 缩写和首字母缩略词
- **general**: 通用术语
- **quantitative**: 包含数字或度量的术语

## 🛡️ 错误处理

API使用标准的HTTP状态码：

- **200**: 成功
- **400**: 请求参数错误（如空文本、无效语言等）
- **500**: 服务器内部错误

错误响应格式：
```json
{
  "detail": "错误描述信息"
}
```

## 🧪 测试

```bash
# 启动API服务
python -m semantic_toolkit.api

# 在另一个终端运行示例
python api_example.py
```

## 📦 生产部署建议

### 使用uvicorn

```bash
uvicorn semantic_toolkit.api:app --host 0.0.0.0 --port 8000
```

### 使用gunicorn

```bash
gunicorn semantic_toolkit.api:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

### Docker部署

```dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY . .
RUN uv sync

EXPOSE 8000

CMD ["uvicorn", "semantic_toolkit.api:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 📝 API规范

完整的API规范和交互式文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🤝 贡献

欢迎贡献代码、报告问题或提出新功能建议！

## 📄 许可证

[添加您的许可证信息]

## 📞 支持

如有问题，请通过以下方式联系：
- GitHub Issues: https://github.com/im-zhong/semantic-toolkit/issues
- Email: [您的邮箱]
