"""
中文基金项目语步识别工具 - Flask后端
调用GLM-4 API进行语步识别
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
    "basis": "立项依据",
    "objective": "研究目标",
    "content": "研究内容",
    "approach": "技术路线/实施方案",
    "expected_result": "预期成果",
    "application_value": "应用价值"
}

# 提示词模板
PROMPT_TEMPLATE = """请分析以下中文基金项目文本，识别每个句子所属的语步类别。

语步类别：
1. basis（立项依据）：项目背景、必要性、研究现状
2. objective（研究目标）：项目目标、预期效果
3. content（研究内容）：研究任务、工作分解
4. approach（技术路线）：技术方案、实施路径
5. expected_result（预期成果）：成果形式、数量指标
6. application_value（应用价值）：应用前景、社会效益

待分析文本：
{text}

请逐句分析，输出格式如下（每行一个句子）：
句子内容|||语步标签
句子内容|||语步标签

关键注意事项：
1. 务必识别文本中的所有句子，不要遗漏任何句子
2. 语步标签只能是：basis、objective、content、approach、expected_result、application_value
3. 保持句子完整性，不要修改或合并句子
4. 每个句子只能归为一个语步类别
5. 如果句子难以分类，选择最符合的一个
6. 保持分类一致性，对相似内容使用相同标准
7. 系统地处理每个句子，确保完整覆盖"""


def parse_result_text(text: str) -> dict:
    """解析模型返回的文本结果"""
    sentences = []

    # 先去除markdown代码块标记
    cleaned_text = text.strip()
    if cleaned_text.startswith('```'):
        first_newline = cleaned_text.find('\n')
        if first_newline != -1:
            cleaned_text = cleaned_text[first_newline + 1:]
        if cleaned_text.endswith('```'):
            cleaned_text = cleaned_text[:-3]
        cleaned_text = cleaned_text.strip()

    # 按行分割
    lines = cleaned_text.split('\n')

    for line in lines:
        line = line.strip()
        if not line or '|||' not in line:
            continue

        # 分割句子内容和标签
        parts = line.split('|||')
        if len(parts) >= 2:
            sentence = parts[0].strip()
            label = parts[1].strip()

            # 验证标签有效性
            valid_labels = ['basis', 'objective', 'content', 'approach', 'expected_result', 'application_value']
            if label in valid_labels and sentence:
                sentences.append({
                    "句子内容": sentence,
                    "语步标签": label
                })

    return {"sentences": sentences}


def analyze_project_text(api_key: str, text: str) -> dict:
    """调用GLM-4 API分析项目语步"""
    try:
        client = ZhipuAI(api_key=api_key)
        prompt = PROMPT_TEMPLATE.format(text=text)

        response = client.chat.completions.create(
            model="glm-4",
            messages=[
                {"role": "system", "content": "你是基金项目分析专家。你的任务是一致地分类项目文本中的所有句子。要全面系统，不要跳过或遗漏任何句子。严格按照指定格式输出结果。必须完整输出所有句子的分类结果，不能中途停止。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,  # 保持低温以获得一致结果
            max_tokens=8192  # 大幅增加输出长度以支持更长的项目文本
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
            print("警告: 输出因长度限制被截断，可能需要处理更长的文本")

        # 解析结果
        result = parse_result_text(result_text)
        if result['sentences']:
            return result

        return {"sentences": [], "raw": result_text}

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        raise e


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json(force=True)
        text = data.get('text', '')

        if not text:
            return jsonify({'error': '请输入文本内容'}), 400

        result = analyze_project_text(API_KEY, text)
        return jsonify(result)

    except Exception as e:
        print(f"API错误: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/labels', methods=['GET'])
def get_labels():
    return jsonify(MOVE_LABELS)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)
