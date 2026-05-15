@echo off
cd /d "%~dp0\.."

echo 正在运行自动分类工具测试...
python -m pytest

pause