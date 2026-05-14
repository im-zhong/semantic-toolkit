@echo off
cd /d "%~dp0\.."

echo 正在启动自动分类工具 API 服务...
echo API文档地址: http://127.0.0.1:8000/docs
echo 健康检查地址: http://127.0.0.1:8000/health

python -m uvicorn auto_classifier.main:app --host 0.0.0.0 --port 8000 --reload

pause