# 中文基金项目语步识别工具

基于GLM4大模型的基金项目文本语步自动识别工具，通过提示词工程实现对立项依据、研究目标、研究内容、技术路线、预期成果、应用价值的自动标注。

## 功能特点

- 自动识别基金项目文本中的6种语步类型
- 可视化高亮展示识别结果
- 统计各语步数量分布
- 简洁易用的Web界面

## 安装步骤

### 1. 安装Python依赖

```bash
pip install -r requirements.txt
```

### 2. 获取API Key

访问 [智谱AI开放平台](https://open.bigmodel.cn/) 注册并获取API Key。

### 3. 启动服务

```bash
python app.py
```

### 4. 访问应用

打开浏览器访问: http://localhost:5002

## 使用方法

1. 在界面中输入您的智谱AI API Key
2. 粘贴中文基金项目文本内容
3. 点击"开始识别"按钮
4. 查看识别结果，不同语步以不同颜色高亮显示

## 语步类型说明

| 标签 | 中文含义 | 说明 |
|------|----------|------|
| basis | 立项依据 | 介绍项目立项的背景、必要性、研究现状、存在问题等 |
| objective | 研究目标 | 说明项目的总体目标、具体目标或预期达到的效果 |
| content | 研究内容 | 描述项目的主要研究内容、研究任务或工作分解 |
| approach | 技术路线 | 阐述技术方案、实施路径、研究方法或技术手段 |
| expected_result | 预期成果 | 列出项目预期产出的成果形式、数量或质量指标 |
| application_value | 应用价值 | 说明项目的应用前景、社会效益、经济效益或推广价值 |

## 项目结构

```
zh_project_move_recognition/
├── app.py              # Flask后端服务
├── requirements.txt    # Python依赖
├── templates/
│   └── index.html      # Web前端页面
└── README.md           # 使用说明
```

## 技术栈

- **后端**: Python + Flask
- **AI模型**: 智谱GLM-4 (通过zhipuai SDK调用)
- **前端**: HTML + CSS + JavaScript
- **核心技术**: 提示词工程 (Prompt Engineering)
