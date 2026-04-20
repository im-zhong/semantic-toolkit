"""
English Abstract Move Recognition Tool - Flask Backend
Calls GLM-4 API for move recognition
"""

import os
import re
import json
from flask import Flask, request, jsonify, render_template
from zhipuai import ZhipuAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# ==================== Configuration ====================
API_KEY = os.getenv("ZHIPU_API_KEY")
if not API_KEY:
    raise ValueError("API key not found. Please set environment variable ZHIPU_API_KEY")
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
PROMPT_TEMPLATE = """Please analyze the following English scientific abstract and identify its move structure.

【Abstract to Analyze】
{abstract}

【Task Requirements】
Identify sentences belonging to each of the following five move types:
1. BACKGROUND: Introduces research field status, existing problems, research importance
2. PURPOSE: States the problems to solve, objectives, innovations
3. METHOD: Describes methods, techniques, experimental design
4. RESULT: Shows research findings, experimental results, performance metrics
5. CONCLUSION: Summarizes contributions, significance, future outlook

【Output Format】
Please strictly output in the following JSON format, do not output any other content:
{{"background": ["sentence1", "sentence2"], "purpose": ["sentence1"], "method": ["sentence1", "sentence2"], "result": ["sentence1"], "conclusion": ["sentence1"]}}

【Critical Requirements】
1. Extract original sentences directly, keep them complete
2. If a move type does not exist, use empty array []
3. Each sentence should be classified into only one primary move
4. Output JSON only, do not output any other text
5. CRITICAL: Make sure to identify ALL sentences in the abstract, do not omit any sentences
6. Be consistent in your classification - use the same criteria for all sentences
7. Process the abstract sentence by sentence, ensure complete coverage"""


def parse_sentences(text: str) -> dict:
    """Parse JSON response and convert to sentence format"""
    sentences = []

    # Remove markdown code blocks if present
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*', '', text)

    # Move category mapping
    move_mapping = {
        "background": "BACKGROUND",
        "purpose": "PURPOSE",
        "method": "METHOD",
        "result": "RESULT",
        "conclusion": "CONCLUSION"
    }

    # Extract sentences for each move category
    for key, label in move_mapping.items():
        # Match "key": ["sentence1", "sentence2", ...] pattern
        pattern = rf'"{key}"\s*:\s*\[(.*?)\]'
        match = re.search(pattern, text, re.DOTALL)

        if match:
            array_content = match.group(1)
            # Extract all quoted strings
            extracted_sentences = re.findall(r'"([^"]*)"', array_content)
            for sentence in extracted_sentences:
                sentence = sentence.strip()
                if sentence:
                    sentences.append({
                        "sentence": sentence,
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
                {"role": "system", "content": "You are a professional scientific literature analysis expert. Your task is to consistently classify ALL sentences in the abstract. Be thorough and systematic - do not skip or omit any sentences. Output only JSON format."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,  # Lower temperature for more consistent results
            max_tokens=4096  # Increase output length for longer abstracts
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
