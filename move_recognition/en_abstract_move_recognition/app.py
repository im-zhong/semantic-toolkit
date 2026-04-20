"""
English Abstract Move Recognition Tool - Flask Backend
Calls GLM-4 API for move recognition
"""

import os
import re
import json
from flask import Flask, request, jsonify, render_template
from zhipuai import ZhipuAI

app = Flask(__name__)

# ==================== Configuration ====================
API_KEY = "e22625d698da4312892b3466ba2aceac.omDODZnT0M0DQNHO"
# =======================================================

# Move label definitions
MOVE_LABELS = {
    "BACKGROUND": "Research background, current status, problems, or motivation",
    "PURPOSE": "Research objectives, problems to solve, or hypotheses",
    "METHOD": "Research methods, experimental design, or techniques",
    "RESULT": "Research findings, experimental results, or data analysis",
    "CONCLUSION": "Conclusions, contributions, significance, or future outlook"
}

# Prompt template for English abstracts
PROMPT_TEMPLATE = """You are an expert in analyzing scientific literature abstracts. Please analyze the following English abstract and identify the move category for each sentence.

Move Category Definitions:
1. BACKGROUND: Introduces the research field background, current status, existing problems, or research motivation
2. PURPOSE: States the research objectives, problems to solve, or hypotheses to verify
3. METHOD: Describes the research methods, experimental design, data sources, or technical approaches
4. RESULT: Presents the research findings, experimental results, or data analysis outcomes
5. CONCLUSION: Summarizes the conclusions, contributions, significance, or future outlook

Abstract to analyze:
{abstract}

Please output the result in the following JSON format, where each sentence contains "sentence" and "move_label" fields:
{{
    "sentences": [
        {{"sentence": "xxx", "move_label": "BACKGROUND/PURPOSE/METHOD/RESULT/CONCLUSION"}},
        ...
    ]
}}

Note:
1. Strictly follow the JSON format
2. Move labels must be one of the 5 English labels above
3. Keep sentences complete, do not omit or merge sentences
4. If a sentence contains multiple move information, choose the most prominent one"""


def parse_sentences(text: str) -> dict:
    """Use regex to extract sentences and labels"""
    sentences = []

    # Match "sentence": "xxx", "move_label": "yyy" pattern
    pattern = r'"sentence"\s*:\s*"([^"]+)"\s*,\s*"move_label"\s*:\s*"(\w+)"'
    matches = re.findall(pattern, text)

    for content, label in matches:
        content = content.strip()
        label = label.strip()

        valid_labels = ['BACKGROUND', 'PURPOSE', 'METHOD', 'RESULT', 'CONCLUSION']
        if label in valid_labels and content:
            sentences.append({
                "sentence": content,
                "move_label": label
            })

    return {"sentences": sentences}


def analyze_abstract(api_key: str, abstract: str) -> dict:
    """Call GLM-4 API to analyze abstract moves"""
    client = ZhipuAI(api_key=api_key)

    prompt = PROMPT_TEMPLATE.format(abstract=abstract)

    try:
        response = client.chat.completions.create(
            model="glm-4",
            messages=[
                {"role": "system", "content": "You are a professional scientific literature analysis expert, skilled in identifying move structures in academic abstracts."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
        )

        result_text = response.choices[0].message.content
        print("=" * 50)
        print("API Response:")
        print(result_text)
        print("=" * 50)

        # Use regex to extract
        result = parse_sentences(result_text)
        if result['sentences']:
            return result

        return {"raw_response": result_text, "sentences": []}

    except Exception as e:
        raise Exception(f"API call failed: {str(e)}")


@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Analysis API endpoint"""
    try:
        data = request.get_json()
        abstract = data.get('abstract', '')

        if not abstract:
            return jsonify({'error': 'Please enter abstract content'}), 400

        result = analyze_abstract(API_KEY, abstract)
        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/labels', methods=['GET'])
def get_labels():
    """Get move label definitions"""
    return jsonify(MOVE_LABELS)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
