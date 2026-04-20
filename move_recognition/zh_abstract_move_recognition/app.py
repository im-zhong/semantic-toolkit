"""
中文摘要语步识别工具 - Flask后端
调用GLM5 API进行语步识别
"""

import os
import re
import json
from flask import Flask, request, jsonify, render_template
from zhipuai import ZhipuAI
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

app = Flask(__name__)

# ==================== 配置区 ====================
API_KEY = os.getenv("ZHIPU_API_KEY")
if not API_KEY:
    raise ValueError("未找到API密钥，请设置环境变量 ZHIPU_API_KEY")
# ================================================

# 语步标签定义
MOVE_LABELS = {
    "BACKGROUND": "研究背景",
    "PURPOSE": "研究目的",
    "METHOD": "研究方法",
    "RESULT": "研究结果",
    "CONCLUSION": "研究结论"
}

# 提示词模板
PROMPT_TEMPLATE = """你是一位科技文献摘要分析专家。请分析以下中文摘要，识别每个句子所属的语步类别。

语步类别定义：
1. 研究背景(BACKGROUND)：介绍研究领域的背景、现状、存在的问题或研究动机
2. 研究目的(PURPOSE)：说明本研究的目标、要解决的问题或要验证的假设
3. 研究方法(METHOD)：描述采用的研究方法、实验设计、数据来源或技术手段
4. 研究结果(RESULT)：呈现研究发现、实验结果、数据分析结果
5. 研究结论(CONCLUSION)：总结研究结论、贡献、意义或未来展望

待分析摘要：
{abstract}

请按以下JSON格式输出结果，每个句子包含"句子内容"和"语步标签"两个字段：
{{
    "sentences": [
        {{"句子内容": "xxx", "语步标签": "BACKGROUND/PURPOSE/METHOD/RESULT/CONCLUSION"}},
        ...
    ]
}}

注意：
1. 严格按照JSON格式输出
2. 语步标签只能使用上述5种英文标签之一
3. 保持句子完整性，不要遗漏或合并句子
4. 如果一个句子包含多个语步信息，选择最主要的一个"""


def parse_sentences(text: str) -> dict:
    """使用正则表达式提取句子和标签"""
    sentences = []

    # 匹配 "句子内容": "xxx", "语步标签": "yyy" 模式
    # 使用非贪婪匹配和更宽松的正则
    pattern = r'"句子内容"\s*:\s*"([^"]+)"\s*,\s*"\s*语步标签\s*"\s*:\s*"\s*(\w+)\s*"'
    matches = re.findall(pattern, text)

    for content, label in matches:
        # 清理内容中的空白
        content = content.strip()
        label = label.strip()

        # 验证标签有效性
        valid_labels = ['BACKGROUND', 'PURPOSE', 'METHOD', 'RESULT', 'CONCLUSION']
        if label in valid_labels and content:
            sentences.append({
                "句子内容": content,
                "语步标签": label
            })

    return {"sentences": sentences}


def analyze_abstract(api_key: str, abstract: str) -> dict:
    """调用GLM5 API分析摘要语步"""
    client = ZhipuAI(api_key=api_key)

    # 构建提示词
    prompt = PROMPT_TEMPLATE.format(abstract=abstract)

    try:
        response = client.chat.completions.create(
            model="glm-4",
            messages=[
                {"role": "system", "content": "你是一位专业的科技文献分析专家，擅长识别学术摘要中的语步结构。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
        )

        result_text = response.choices[0].message.content

        # 使用正则提取
        result = parse_sentences(result_text)
        if result['sentences']:
            return result

        return {"raw_response": result_text, "sentences": []}

    except Exception as e:
        raise Exception(f"API调用失败: {str(e)}")


@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


@app.route('/test')
def test():
    """测试页面 - 直接显示所有结果"""
    return render_template('test_direct_display.html')


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """分析接口"""
    try:
        data = request.get_json()
        abstract = data.get('abstract', '')

        if not abstract:
            return jsonify({'error': '请输入摘要内容'}), 400

        result = analyze_abstract(API_KEY, abstract)
        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/labels', methods=['GET'])
def get_labels():
    """获取语步标签定义"""
    return jsonify(MOVE_LABELS)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
