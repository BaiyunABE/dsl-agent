#!/bin/bash

# DSL客服机器人测试脚本

echo "🧪 DSL客服机器人测试套件"
echo "================================"

# 设置Python路径
export PYTHONPATH=src:$PYTHONPATH

# 检查测试数据文件
if [ ! -f "test_data/order.csv" ]; then
    echo "❌ 测试数据文件不存在，请先创建测试数据"
    exit 1
fi

# 运行单元测试
echo "📋 运行单元测试..."
python -m pytest test_*.py -v --tb=short

if [ $? -eq 0 ]; then
    echo "✅ 单元测试通过"
else
    echo "❌ 单元测试失败"
    exit 1
fi

# 运行集成测试
echo "🔗 运行集成测试..."
python -m pytest test_integration.py -v -m integration

if [ $? -eq 0 ]; then
    echo "✅ 集成测试通过"
else
    echo "❌ 集成测试失败"
    exit 1
fi

# 运行性能测试
echo "⚡ 运行性能测试..."
python test_runner.py --performance

echo "🎉 所有测试完成！"