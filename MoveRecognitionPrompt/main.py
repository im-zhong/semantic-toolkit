"""
语义计算工具库 - 统一服务器
同时提供 Gradio 首页和 ModelScope 风格功能页面
"""

import os
import multiprocessing
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 导入语步识别服务
from services.move_recognition import (
    analyze_zh_abstract,
    analyze_en_abstract,
    analyze_zh_project
)

# ==================== Flask 应用 ====================

flask_app = Flask(__name__, static_folder='frontend', static_url_path='/frontend')
CORS(flask_app)


# ==================== API 路由 ====================

@flask_app.route('/api/move-recognition/chinese-abstract', methods=['POST'])
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


@flask_app.route('/api/move-recognition/english-abstract', methods=['POST'])
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


@flask_app.route('/api/move-recognition/chinese-project', methods=['POST'])
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

@flask_app.route('/')
def index():
    """重定向到 Gradio 首页"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <meta http-equiv="refresh" content="0;url=http://127.0.0.1:7862">
        <title>重定向中...</title>
    </head>
    <body>
        <p>正在跳转到 <a href="http://127.0.0.1:7862">语义计算工具库</a>...</p>
    </body>
    </html>
    '''


def run_flask():
    """运行 Flask 服务"""
    flask_app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)


def run_gradio():
    """运行 Gradio 服务"""
    import gradio as gr
    from app import demo, CUSTOM_CSS, APP_JS_SCRIPT

    frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")
    demo.launch(
        server_name="127.0.0.1",
        server_port=7862,
        share=False,
        css=CUSTOM_CSS,
        head=APP_JS_SCRIPT,
        allowed_paths=[frontend_dir]
    )


if __name__ == '__main__':
    print("=" * 60)
    print("语义计算工具库 - 统一服务")
    print("=" * 60)
    print()
    print("Gradio 首页: http://127.0.0.1:7862")
    print()
    print("ModelScope 风格功能页面:")
    print("  - http://127.0.0.1:5000/frontend/zh-abstract.html (中文摘要)")
    print("  - http://127.0.0.1:5000/frontend/en-abstract.html (英文摘要)")
    print("  - http://127.0.0.1:5000/frontend/zh-project.html (基金项目)")
    print()
    print("API 接口:")
    print("  - POST http://127.0.0.1:5000/api/move-recognition/chinese-abstract")
    print("  - POST http://127.0.0.1:5000/api/move-recognition/english-abstract")
    print("  - POST http://127.0.0.1:5000/api/move-recognition/chinese-project")
    print()
    print("提示: 在首页点击导航会跳转到 ModelScope 风格页面")
    print("=" * 60)

    # 使用进程运行 Flask
    flask_process = multiprocessing.Process(target=run_flask)
    flask_process.start()

    # 主进程运行 Gradio（会阻塞）
    try:
        run_gradio()
    finally:
        flask_process.terminate()
