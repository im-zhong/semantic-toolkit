# 中文摘要语步识别工具

基于GLM5大模型的科技文献摘要语步自动识别工具，通过提示词工程实现对研究背景、研究目的、研究方法、研究结果、研究结论的自动标注。

## 功能特点

- 自动识别中文摘要中的5种语步类型
- 可视化高亮展示识别结果
- 统计各语步数量分布
- 简洁易用的Web界面

## 安装步骤

### 1. 安装Python依赖

```bash
pip install -r requirements.txt
```

### 2. 配置API Key

**方法1: 使用环境变量（推荐，更安全）**
```bash
# 临时设置（当前会话有效）
export ZHIPU_API_KEY="your_actual_api_key_here"

# 永久设置（添加到 ~/.bashrc）
echo 'export ZHIPU_API_KEY="your_actual_api_key_here"' >> ~/.bashrc
source ~/.bashrc
```

**方法2: 使用 .env 文件**
```bash
# 复制示例配置文件
cp .env.example .env

# 编辑 .env 文件，填入您的 API 密钥
nano .env
```

⚠️ **安全提示**: 不要将真实的 API 密钥提交到 Git 仓库。`.env` 文件已在 .gitignore 中排除。

### 3. 获取API Key

访问 [智谱AI开放平台](https://open.bigmodel.cn/) 注册并获取API Key。

### 4. 启动服务

```bash
python app.py
```

### 5. 访问应用

打开浏览器访问: http://localhost:5000

## 使用方法

1. 在界面中输入您的智谱AI API Key
2. 粘贴中文科技文献摘要内容
3. 点击"开始识别"按钮
4. 查看识别结果，不同语步以不同颜色高亮显示

## 语步类型说明

| 标签 | 中文含义 | 说明 |
|------|----------|------|
| BACKGROUND | 研究背景 | 介绍研究领域背景、现状、问题或动机 |
| PURPOSE | 研究目的 | 说明研究目标、要解决的问题或假设 |
| METHOD | 研究方法 | 描述研究方法、实验设计或技术手段 |
| RESULT | 研究结果 | 呈现研究发现、实验结果或数据分析结果 |
| CONCLUSION | 研究结论 | 总结研究结论、贡献或未来展望 |

## 项目结构

```
zh_abstract_move_recognition/
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
