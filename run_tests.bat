@echo off
chcp 65001 >nul
echo ========================================
echo 运行中图分类法项目单元测试
echo ========================================
echo.

echo 正在安装/更新依赖...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo 依赖安装失败！
    pause
    exit /b 1
)

echo.
echo ========================================
echo 运行所有测试
echo ========================================
pytest -v

echo.
echo ========================================
echo 测试完成
echo ========================================
pause
