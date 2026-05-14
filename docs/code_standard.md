# 代码规范说明

## 1. 项目目录规范

本项目后端代码按照 FastAPI 多文件结构进行组织，主要目录如下：
sem_cal/
├── app/
│   ├── __init__.py
│   ├── main.py                         # FastAPI 项目主入口，负责创建 app、注册路由、配置中间件
│   ├── dependencies.py                 # 公共依赖，例如 Token 校验、公共 Header 校验、分页参数等
│   ├── config.py                       # 项目配置，例如模型名称、默认参数、文件路径、环境变量读取
│   ├── exceptions.py                   # 自定义异常和统一异常处理
│   ├── routers/                        # 接口路由层：只负责接收请求、调用 service、返回结果
│   │   ├── __init__.py
│   │   ├── classify.py                 # 自动分类工具接口
│   │   ├── keyword.py                  # 关键词识别工具接口
│   │   ├── semantic_similarity.py      # 语义相似度计算接口
│   │   ├── topic_mining.py             # 主题挖掘工具接口
│   │   ├── abstract_review.py          # 结构化自动综述工具接口
│   │   ├── entity_extract.py           # 实体识别 / 实体抽取接口
│   │   ├── sentiment.py                # 情感分析 / 倾向性分析接口
│   │   ├── file_parse.py               # 文件上传、文本解析接口
│   │   └── health.py                   # 服务健康检查接口
│   ├── schemas/                        # 数据模型层：定义请求参数和响应结果
│   │   ├── __init__.py
│   │   ├── classify.py                 # 自动分类请求体、响应体模型
│   │   ├── keyword.py                  # 关键词识别请求体、响应体模型
│   │   ├── semantic_similarity.py      # 语义相似度请求体、响应体模型
│   │   ├── topic_mining.py             # 主题挖掘请求体、响应体模型
│   │   ├── abstract_review.py          # 自动综述请求体、响应体模型
│   │   ├── entity_extract.py           # 实体抽取请求体、响应体模型
│   │   ├── sentiment.py                # 情感分析请求体、响应体模型
│   │   └── common.py                   # 通用响应格式、分页结构、错误响应结构
│   ├── services/                       # 业务逻辑层：处理核心业务，不直接写接口路径
│   │   ├── __init__.py
│   │   ├── classify_service.py         # 自动分类业务逻辑
│   │   ├── keyword_service.py          # 关键词识别业务逻辑
│   │   ├── semantic_similarity_service.py
│   │   ├── topic_mining_service.py
│   │   ├── abstract_review_service.py
│   │   ├── entity_extract_service.py
│   │   ├── sentiment_service.py
│   │   └── file_parse_service.py
│   ├── core/                           # 核心能力封装层：模型调用、算法调用、通用计算能力
│   │   ├── __init__.py
│   │   ├── model_client.py             # 大模型调用封装，例如智谱、OpenAI、本地模型等
│   │   ├── embedding_client.py         # 向量模型、Embedding 模型调用封装
│   │   ├── text_processor.py           # 文本清洗、分词、去重、长度截断等
│   │   ├── prompt_templates.py         # 提示词模板统一管理
│   │   └── algorithm_registry.py       # 算法注册与调用管理
│   ├── algorithms/                     # 具体算法实现层
│   │   ├── __init__.py
│   │   ├── classify_algorithm.py       # 自动分类算法
│   │   ├── keyword_algorithm.py        # 关键词提取算法
│   │   ├── similarity_algorithm.py     # 相似度计算算法
│   │   ├── topic_algorithm.py          # 主题挖掘算法
│   │   ├── summary_algorithm.py        # 自动综述算法
│   │   ├── entity_algorithm.py         # 实体识别算法
│   │   └── sentiment_algorithm.py      # 情感分析算法
│   ├── data/                           # 项目内置数据、分类体系、词表等
│   │   ├── clc_categories.json         # 中图分类法类目数据
│   │   ├── stopwords.txt               # 停用词表
│   │   ├── domain_keywords.json        # 专业领域关键词词表
│   │   └── README.md                   # 数据文件说明
│   ├── utils/                          # 工具函数层：与具体业务无强绑定的通用工具
│   │   ├── __init__.py
│   │   ├── response.py                 # 统一响应结果封装
│   │   ├── logger.py                   # 日志工具
│   │   ├── file_utils.py               # 文件读取、保存、格式判断
│   │   ├── text_utils.py               # 文本处理工具
│   │   ├── validators.py               # 参数校验工具
│   │   └── time_utils.py               # 时间处理工具
│   └── internal/                       # 内部管理接口，不对普通用户开放
│       ├── __init__.py
│       ├── admin.py                    # 管理员接口
│       ├── monitor.py                  # 服务监控接口
│       └── task_manage.py              # 后台任务管理接口
├── tests/                              # 单元测试目录
│   ├── __init__.py
│   ├── test_classify.py                # 自动分类工具测试
│   ├── test_keyword.py                 # 关键词识别工具测试
│   ├── test_semantic_similarity.py     # 语义相似度测试
│   ├── test_topic_mining.py            # 主题挖掘测试
│   ├── test_abstract_review.py         # 自动综述测试
│   ├── test_file_parse.py              # 文件解析测试
│   └── test_health.py                  # 健康检查测试
├── docs/                               # 项目文档目录
│   ├── api.md                          # 接口说明文档
│   ├── code_standard.md                # 代码规范文档
│   ├── deployment.md                   # 部署说明文档
│   └── module_design.md                # 模块设计说明文档
├── scripts/                            # 辅助脚本目录
│   ├── run_dev.py                      # 本地开发启动脚本
│   ├── init_data.py                    # 初始化数据脚本
│   └── check_env.py                    # 环境检查脚本
├── logs/                               # 日志目录，实际日志文件不建议提交到 Git
│   └── .gitkeep
├── .env.example                        # 环境变量示例文件，可以提交
├── .gitignore                          # Git 忽略文件
├── requirements.txt                    # Python 第三方依赖
├── README.md                           # 项目说明文档
└── CONTRIBUTING.md                     # 团队协作与提交规范
