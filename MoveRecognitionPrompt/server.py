"""
语义计算工具库 - Web 服务器
提供语步识别 API 和 ModelScope 风格的静态页面
"""

import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# 导入语步识别服务
from services.move_recognition import (
    analyze_zh_abstract,
    analyze_en_abstract,
    analyze_zh_project
)

app = Flask(__name__, static_folder='frontend', static_url_path='/frontend')
CORS(app)


# ==================== API 路由 ====================

@app.route('/api/move-recognition/chinese-abstract', methods=['POST'])
def api_chinese_abstract():
    """中文摘要语步识别 API"""
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({"code": 400, "message": "缺少 text 参数", "data": None})
        result = analyze_zh_abstract(data['text'])
        return jsonify(result)
    except Exception as e:
        return jsonify({"code": 500, "message": f"服务错误: {str(e)}", "data": None})


@app.route('/api/move-recognition/english-abstract', methods=['POST'])
def api_english_abstract():
    """英文摘要语步识别 API"""
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({"code": 400, "message": "Missing 'text' parameter", "data": None})
        result = analyze_en_abstract(data['text'])
        return jsonify(result)
    except Exception as e:
        return jsonify({"code": 500, "message": f"Server error: {str(e)}", "data": None})


@app.route('/api/move-recognition/chinese-project', methods=['POST'])
def api_chinese_project():
    """中文基金项目语步识别 API"""
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({"code": 400, "message": "缺少 text 参数", "data": None})
        result = analyze_zh_project(data['text'])
        return jsonify(result)
    except Exception as e:
        return jsonify({"code": 500, "message": f"服务错误: {str(e)}", "data": None})


# ==================== 页面路由 ====================

@app.route('/')
def index():
    """重定向到 Gradio 首页"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>语义计算工具库</title>
        <style>
            body { font-family: "Microsoft YaHei", sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; background: #f7f9fc; }
            .container { text-align: center; padding: 40px; background: white; border-radius: 20px; box-shadow: 0 10px 40px rgba(0,0,0,0.1); }
            h1 { color: #2563ff; margin-bottom: 20px; }
            p { color: #64748b; margin-bottom: 30px; }
            .links { display: flex; gap: 15px; justify-content: center; flex-wrap: wrap; }
            a { display: block; padding: 15px 25px; background: linear-gradient(135deg, #5fa8ff, #3b82ff); color: white; text-decoration: none; border-radius: 12px; font-weight: 600; transition: transform 0.2s; }
            a:hover { transform: translateY(-2px); }
            .secondary { background: white; color: #2563ff; border: 2px solid #e2e8f0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>语义计算工具库</h1>
            <p>选择功能开始使用</p>
            <div class="links">
                <a href="/frontend/zh-abstract.html">中文摘要语步识别</a>
                <a href="/frontend/en-abstract.html">英文摘要语步识别</a>
                <a href="/frontend/zh-project.html">基金项目语步识别</a>
            </div>
            <div style="margin-top: 30px;">
                <a href="http://127.0.0.1:7862" class="secondary" target="_blank">打开 Gradio 首页</a>
            </div>
        </div>
    </body>
    </html>
    '''


@app.route('/health')
def health():
    """健康检查"""
    return jsonify({"status": "ok"})


if __name__ == '__main__':
    print("=" * 60)
    print("语义计算工具库 - 语步识别 Web 服务")
    print("=" * 60)
    print()
    print("ModelScope 风格页面:")
    print("  - http://127.0.0.1:5000 (功能选择)")
    print("  - http://127.0.0.1:5000/frontend/zh-abstract.html (中文摘要)")
    print("  - http://127.0.0.1:5000/frontend/en-abstract.html (英文摘要)")
    print("  - http://127.0.0.1:5000/frontend/zh-project.html (基金项目)")
    print()
    print("Gradio 首页: http://127.0.0.1:7862")
    print()
    print("API 接口:")
    print("  - POST http://127.0.0.1:5000/api/move-recognition/chinese-abstract")
    print("  - POST http://127.0.0.1:5000/api/move-recognition/english-abstract")
    print("  - POST http://127.0.0.1:5000/api/move-recognition/chinese-project")
    print()
    print("=" * 60)

    app.run(host='127.0.0.1', port=5000, debug=True)
