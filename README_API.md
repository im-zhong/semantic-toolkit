# 中图分类法科技文献自动分类 - API文档

## 📦 安装依赖

```bash
pip install -r requirements.txt
```

## 🧪 运行单元测试

### 运行所有测试
```bash
pytest
```

### 运行特定测试文件
```bash
# 测试CLI模块
pytest test_cli.py -v

# 测试分类器核心模块
pytest test_clc_classifier.py -v
```

### 运行测试并生成覆盖率报告
```bash
pytest --cov=. --cov-report=html
```

### 运行特定测试用例
```bash
# 测试中文分类功能
pytest test_clc_classifier.py::TestCLCAutoClassifier::test_classify_chinese -v

# 测试文本截断功能
pytest test_clc_classifier.py::TestUtilityFunctions::test_truncate_text -v
```

### 测试参数说明
- `-v`: 详细输出
- `-s`: 显示print输出
- `--cov=模块名`: 指定要计算覆盖率的模块
- `--cov-report=html`: 生成HTML格式的覆盖率报告
- `-k 关键词`: 只运行包含关键词的测试

## 🚀 启动FastAPI服务

### 方式一：直接运行
```bash
python api.py
```

### 方式二：使用uvicorn
```bash
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

服务启动后，访问：
- API文档: http://localhost:8000/docs
- ReDoc文档: http://localhost:8000/redoc
- 健康检查: http://localhost:8000/health

## 📡 API接口说明

### 1. 文本分类接口

**请求方式**: `POST /api/v1/classify`

**请求体**:
```json
{
  "text": "本文研究了深度学习在医学影像诊断中的应用",
  "mode": "zh",
  "domain_hint": "人工智能"
}
```

**参数说明**:
- `text` (必填): 待分类的文本内容
- `mode` (必填): 分类模式
  - `zh`: 中文科技文献分类
  - `en`: 英文科技文献分类
  - `domain`: 专业领域科技文献分类
- `domain_hint` (可选): 专业领域提示，domain模式推荐填写
> `model` 和 `top_k` 是后端固定配置，不作为接口入参暴露给用户。

**响应示例**:
```json
{
  "tool": "自动分类工具",
  "mode": "中文科技文献分类",
  "model": "glm-4-flash",
  "category_source": "data/完整版中国图书馆图书分类法.json",
  "loaded_scitech_categories": 2105,
  "candidate_count": 80,
  "result": {
    "language_detected": "zh",
    "is_interdisciplinary": false,
    "primary": {
      "id": "TP18",
      "name": "人工智能",
      "path": "T 工业技术 > TP 自动化技术、计算机技术 > TP18 人工智能",
      "confidence": 0.92,
      "reason": "文献主题明确涉及深度学习和医学影像，属于人工智能应用"
    },
    "alternatives": [
      {
        "id": "R445",
        "name": "影像诊断学",
        "path": "R 医药、卫生 > R4 临床医学 > R445 影像诊断学",
        "confidence": 0.75,
        "reason": "涉及医学影像诊断技术"
      }
    ],
    "keywords": ["深度学习", "医学影像", "诊断", "人工智能"],
    "user_selection_note": "主分类用于默认归档；若文献同时强调方法、对象和应用场景，可从备选分类号中人工选择。"
  },
  "local_top_candidates": [...]
}
```

### 2. 文件分类接口

**请求方式**: `POST /api/v1/classify/file`

**请求参数** (multipart/form-data):
- `file`: 文件（支持txt/md/json等文本格式）
- `mode`: 分类模式（必填）
- `domain_hint`: 专业领域提示（可选）
- `encoding`: 文件编码，默认utf-8
> `model` 和 `top_k` 是后端固定配置，不作为接口入参暴露给用户。

**cURL示例**:
```bash
curl -X POST "http://localhost:8000/api/v1/classify/file" \
  -F "file=@document.txt" \
  -F "mode=zh" \
  -F "domain_hint=人工智能" \
  -F "encoding=utf-8"
```

### 3. 健康检查

**请求方式**: `GET /health`

**响应示例**:
```json
{
  "status": "healthy",
  "loaded_categories": 2105,
  "model": "glm-4-flash"
}
```

### 4. 获取分类模式列表

**请求方式**: `GET /api/v1/modes`

**响应示例**:
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
      "description": "基于专业领域提示的深度分类，建议填写domain_hint"
    }
  ]
}
```

### 5. 获取统计信息

**请求方式**: `GET /api/v1/stats`

**响应示例**:
```json
{
  "total_categories": 2105,
  "model": "glm-4-flash",
  "top_k": 80,
  "prompt_candidate_k": 35
}
```

## 🧪 测试示例

### Python示例
```python
import requests

# 文本分类
response = requests.post(
    "http://localhost:8000/api/v1/classify",
    json={
        "text": "本文研究了深度学习在医学影像诊断中的应用",
        "mode": "zh",
        "domain_hint": "人工智能"
    }
)
result = response.json()
print(result)

# 健康检查
health = requests.get("http://localhost:8000/health")
print(health.json())
```

### cURL示例
```bash
# 文本分类
curl -X POST "http://localhost:8000/api/v1/classify" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "本文研究了深度学习在医学影像诊断中的应用",
    "mode": "zh",
    "domain_hint": "人工智能"
  }'

# 健康检查
curl http://localhost:8000/health
```

## 🔧 环境配置

确保配置`.env`文件：
```env
ZHIPUAI_API_KEY=your_api_key_here
ZHIPU_MODEL=glm-4-flash
```

## 📝 测试覆盖率

运行以下命令生成测试覆盖率报告：
```bash
pytest --cov=. --cov-report=html
```

报告将生成在`htmlcov/index.html`，在浏览器中打开即可查看。

## 🐛 常见问题

### 1. 测试失败
- 确保已安装所有依赖：`pip install -r requirements.txt`
- 检查智谱API密钥是否正确配置

### 2. API启动失败
- 检查端口8000是否被占用
- 确保中图分类法JSON文件存在于`data/`目录

### 3. 文件上传失败
- 确保文件是文本格式（txt/md/json）
- 检查文件编码是否正确

## 📚 相关文档

- FastAPI官方文档: https://fastapi.tiangolo.com/
- pytest官方文档: https://docs.pytest.org/
- 智谱AI文档: https://open.bigmodel.cn/dev/api
