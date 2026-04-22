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
PROMPT_TEMPLATE = """Please carefully analyze the following English scientific abstract and identify its move structure sentence by sentence.

【Abstract to Analyze】
{abstract}

【Move Classification Standards】
1. BACKGROUND: Introduces research field status, existing problems, research importance
2. PURPOSE: States the problems to solve, objectives, innovations
3. METHOD: Describes methods, techniques, experimental design
4. RESULT: Shows research findings, experimental results, performance metrics
5. CONCLUSION: Summarizes contributions, significance, future outlook

【Specific Task】
Please process the abstract according to these steps:
1. First, split the abstract into sentences (using periods, question marks, and exclamation marks as delimiters)
2. Then, classify each sentence into a move category
3. Ensure every sentence is classified, do not omit any sentence
4. Organize the results by move type

【Output Format】
Strictly output in the following JSON format, do not output any other content:
{{"background": ["complete sentence 1", "complete sentence 2"], "purpose": ["complete sentence"], "method": ["complete sentence"], "result": ["complete sentence"], "conclusion": ["complete sentence"]}}

【Strict Requirements】
1. MUST identify and classify EVERY sentence in the abstract, omissions are not allowed
2. Use complete original sentences from the text, do not modify or truncate them
3. Each sentence can only be classified into one move category
4. If a move type has no corresponding sentences, use an empty array []
5. Output only JSON, do not add any explanatory text
6. Ensure JSON format is correct with all brackets and quotes matched
7. Include complete sentences even if they are long"""


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
                {"role": "system", "content": "You are a professional scientific literature analysis expert. Your core task is to analyze the abstract sentence by sentence and classify each sentence into a move category. You MUST ensure that you identify and classify EVERY sentence in the abstract, no omissions are allowed. Output strictly in the required JSON format, ensuring each sentence is included in the results."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,  # Lower temperature for more consistent results
            max_tokens=8192  # Significantly increase output length for longer abstracts
        )

        result_text = response.choices[0].message.content
        finish_reason = response.choices[0].finish_reason

        print("=" * 50)
        print("API Response:")
        print(result_text)
        print(f"Finish reason: {finish_reason}")
        print("=" * 50)

        # Check if output was truncated due to length limit
        if finish_reason == "length":
            print("Warning: Output was truncated due to length limit, may need to handle longer abstracts")

        # Use regex to extract
        result = parse_sentences(result_text)
        if result['sentences']:
            print(f"Identified {len(result['sentences'])} sentences")
            # Count sentences per move type
            from collections import Counter
            label_counts = Counter([s['move_label'] for s in result['sentences']])
            print(f"Move distribution: {dict(label_counts)}")
            return result

        print("Warning: Could not extract sentences from response")
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
