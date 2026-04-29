@echo off
chcp 65001 >nul
echo ========================================
echo 启动中图分类法API服务
echo ========================================
echo.

echo 正在检查依赖...
python -c "import fastapi" 2>nul
if %errorlevel% neq 0 (
    echo 正在安装API依赖...
    pip install -r requirements.txt
)

echo.
echo ========================================
echo API服务启动中...
echo ========================================
echo.
echo API文档地址: http://localhost:8000/docs
echo ReDoc地址: http://localhost:8000/redoc
echo 健康检查: http://localhost:8000/health
echo.
echo 按 Ctrl+C 停止服务
echo.

python api.py

pause
