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
PROMPT_TEMPLATE = """请仔细分析以下中文科技论文摘要，逐句识别并分类其中的语步结构。

【待分析摘要】
{abstract}

【语步分类标准】
1. 研究背景(background)：介绍研究领域现状、存在问题、研究重要性
2. 研究目的(purpose)：说明本研究要解决的问题、目标、创新点
3. 研究方法(method)：描述采用的方法、技术、实验设计
4. 研究结果(result)：展示研究发现、实验结果、性能指标
5. 研究结论(conclusion)：总结研究贡献、意义、未来展望

【具体任务】
请按照以下步骤处理：
1. 首先将摘要按句子分割（以句号、问号、感叹号为分隔符）
2. 然后对每个句子进行语步分类
3. 确保每个句子都被分类，不要遗漏任何句子
4. 将分类结果按语步类型组织

【输出格式】
严格按照以下JSON格式输出，不要输出任何其他内容：
{{"background": ["完整的句子1", "完整的句子2"], "purpose": ["完整的句子"], "method": ["完整的句子"], "result": ["完整的句子"], "conclusion": ["完整的句子"]}}

【严格要求】
1. 必须识别并分类摘要中的每一个句子，不允许遗漏
2. 直接使用原文中的完整句子，不要修改或截断
3. 每个句子只能归为一个语步类别
4. 如果某类语步没有对应句子，使用空数组 []
5. 只输出JSON，不要添加任何说明文字
6. 确保JSON格式正确，所有括号和引号都匹配
7. 即使句子很长，也要完整包含在结果中"""


def parse_sentences(text: str) -> dict:
    """解析JSON响应并转换为句子格式"""
    sentences = []

    # 移除markdown代码块标记
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*', '', text)

    # 语步类别映射
    move_mapping = {
        "background": "BACKGROUND",
        "purpose": "PURPOSE",
        "method": "METHOD",
        "result": "RESULT",
        "conclusion": "CONCLUSION"
    }

    # 对每个语步类别，提取对应的句子
    for key, label in move_mapping.items():
        # 匹配 "key": ["句子1", "句子2", ...] 格式
        pattern = rf'"{key}"\s*:\s*\[(.*?)\]'
        match = re.search(pattern, text, re.DOTALL)

        if match:
            array_content = match.group(1)
            # 提取所有引号包围的字符串
            extracted_sentences = re.findall(r'"([^"]*)"', array_content)
            for sentence in extracted_sentences:
                sentence = sentence.strip()
                if sentence:
                    sentences.append({
                        "句子内容": sentence,
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
                {"role": "system", "content": "你是一位专业的科技文献分析专家。你的核心任务是逐句分析摘要，对每个句子进行语步分类。必须确保识别并分类摘要中的每一个句子，不能遗漏任何句子。严格按照要求的JSON格式输出，确保每个句子都包含在结果中。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,  # 降低温度以获得更一致的结果
            max_tokens=8192  # 大幅增加输出长度以支持长摘要
        )

        result_text = response.choices[0].message.content
        finish_reason = response.choices[0].finish_reason

        print("=" * 50)
        print("API返回内容:")
        print(result_text)
        print(f"Finish reason: {finish_reason}")
        print("=" * 50)

        # 检查是否因为长度限制而被截断
        if finish_reason == "length":
            print("警告: 输出因长度限制被截断，可能需要处理更长的摘要")

        # 使用正则提取
        result = parse_sentences(result_text)
        if result['sentences']:
            print(f"识别到 {len(result['sentences'])} 个句子")
            # 统计各语步的句子数量
            from collections import Counter
            label_counts = Counter([s['语步标签'] for s in result['sentences']])
            print(f"各语步句子分布: {dict(label_counts)}")
            return result

        print("警告: 未能从响应中提取到句子")
        return {"raw_response": result_text, "sentences": []}

    except Exception as e:
        raise Exception(f"API调用失败: {str(e)}")


@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


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
