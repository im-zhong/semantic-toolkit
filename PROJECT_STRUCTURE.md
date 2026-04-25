# 项目结构说明

```
clc_zhipu_classifier_project/
│
├── clc_classifier.py          # 核心分类器模块
│   ├── Category               # 分类数据类
│   ├── CategoryStore          # 分类法存储
│   ├── TfidfCandidateRetriever # 本地召回器
│   ├── ZhipuClient            # 智谱AI客户端
│   └── CLCAutoClassifier      # 主分类服务
│
├── cli.py                     # 命令行界面
│   ├── read_text()            # 文本读取
│   └── main()                 # 主函数
│
├── api.py                     # FastAPI接口封装
│   ├── classify_text()        # 文本分类接口
│   ├── classify_file()        # 文件分类接口
│   ├── health_check()         # 健康检查
│   └── 其他辅助接口
│
├── test_cli.py                # CLI模块单元测试
├── test_clc_classifier.py     # 分类器核心模块单元测试
├── test_api.py                # API接口单元测试
├── conftest.py                # Pytest配置和fixtures
├── pytest.ini                 # Pytest配置文件
│
├── requirements.txt           # 项目依赖
├── run_tests.bat              # Windows测试运行脚本
├── run_api.bat                # Windows API启动脚本
├── run_tests.sh               # Linux/Mac测试运行脚本
├── run_api.sh                 # Linux/Mac API启动脚本
│
├── README_API.md              # API使用文档
├── PROJECT_STRUCTURE.md       # 本文件 - 项目结构说明
│
└── data/                      # 数据目录
    └── 完整版中国图书馆图书分类法.json  # 分类法数据（需自行准备）
```

## 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 运行测试
**Windows:**
```bash
run_tests.bat
```

**Linux/Mac:**
```bash
./run_tests.sh
# 或
bash run_tests.sh
```

**手动运行:**
```bash
pytest -v
```

### 3. 启动API服务
**Windows:**
```bash
run_api.bat
```

**Linux/Mac:**
```bash
./run_api.sh
# 或
bash run_api.sh
```

**手动启动:**
```bash
python api.py
# 或
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

### 4. 使用CLI
```bash
# 中文分类
python cli.py --mode zh --text "本文研究了深度学习在医学影像诊断中的应用"

# 英文分类
python cli.py --mode en --text "Deep learning in medical imaging"

# 专业领域分类
python cli.py --mode domain --text "测试文本" --domain-hint "计算机科学"

# 文件分类
python cli.py --mode zh --file document.txt
```

## 模块说明

### 核心模块 (clc_classifier.py)
- **Category**: 分类数据结构，存储分类号、名称、路径等信息
- **CategoryStore**: 加载和管理中图分类法数据
- **TfidfCandidateRetriever**: 基于BM25的本地候选召回
- **ZhipuClient**: 智谱AI API调用封装
- **CLCAutoClassifier**: 主分类服务，提供中英文和专业领域分类

### CLI模块 (cli.py)
- 提供命令行界面
- 支持三种分类模式：zh、en、domain
- 支持文本输入和文件输入
- 输出JSON格式结果

### API模块 (api.py)
- **POST /api/v1/classify**: 文本分类接口
- **POST /api/v1/classify/file**: 文件分类接口
- **GET /health**: 健康检查
- **GET /api/v1/modes**: 获取分类模式列表
- **GET /api/v1/stats**: 获取统计信息

### 测试模块
- **test_cli.py**: 测试CLI功能
- **test_clc_classifier.py**: 测试分类器核心功能
- **test_api.py**: 测试API接口
- **conftest.py**: 提供测试fixtures

## 测试覆盖范围

### test_cli.py
- 文本读取功能（从参数、从文件）
- 错误处理（文件不存在、无输入）
- 三种分类模式
- 自定义参数
- JSON输出格式

### test_clc_classifier.py
- 工具函数（normalize_clc_id、top_letter、clamp、truncate_text）
- Category数据类
- CategoryStore类
- JSON解析
- 查询扩展
- CLCAutoClassifier主类

### test_api.py
- 所有API端点
- 请求参数验证
- 错误处理
- 文件上传
- 不同分类模式

## 配置文件

### .env
需要配置智谱AI API密钥：
```env
ZHIPUAI_API_KEY=your_api_key_here
ZHIPU_MODEL=glm-4-flash
```

### pytest.ini
Pytest配置文件，定义测试规则和标记。

## 注意事项

1. **分类法数据文件**: 需要将"完整版中国图书馆图书分类法.json"放到data/目录
2. **API密钥**: 必须配置智谱AI的API密钥才能使用分类功能
3. **端口**: 默认使用8000端口，确保端口未被占用
4. **编码**: 文件上传时默认使用utf-8编码，可通过参数修改

## 扩展开发

### 添加新的分类模式
1. 在`clc_classifier.py`的`MODE_LABELS`中添加新模式
2. 在`CLCAutoClassifier`中添加对应的分类方法
3. 在API和CLI中添加支持

### 添加新的测试
1. 在对应的测试文件中添加测试函数
2. 使用pytest的fixtures提供测试数据
3. 运行`pytest -v`验证测试通过

### 自定义API端点
1. 在`api.py`中添加新的路由函数
2. 使用FastAPI的依赖注入
3. 添加对应的测试用例
