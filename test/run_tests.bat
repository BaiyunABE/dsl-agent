@echo off
echo 🧪 DSL客服机器人测试套件
echo ================================

:: 设置Python路径
set PYTHONPATH=src;%PYTHONPATH%

:: 检查测试数据文件
if not exist "test_data\order.csv" (
    echo ❌ 测试数据文件不存在，请先创建测试数据
    exit /b 1
)

:: 运行测试
echo 📋 运行测试套件...
python test_runner.py

if %errorlevel% equ 0 (
    echo 🎉 所有测试通过！
) else (
    echo ❌ 测试失败
    exit /b 1
)