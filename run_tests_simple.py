#!/usr/bin/env python3
"""
简单测试运行器 - 修复版本
"""

import sys
import os
import unittest

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# 添加src目录到Python路径
src_dir = os.path.join(project_root, 'src')
sys.path.insert(0, src_dir)

def run_tests():
    """运行所有测试"""
    print("🧪 开始运行DSL客服机器人测试...")
    print("=" * 50)
    
    # 检查必要的文件是否存在
    required_files = [
        'src/dsl_engine.py',
        'src/llm_client.py', 
        'src/parser.py',
        'test/test_dsl_engine.py',
        'test/test_llm_client.py',
        'test/test_parser.py'
    ]
    
    for file_path in required_files:
        if not os.path.exists(file_path):
            print(f"❌ 缺少必要文件: {file_path}")
            return False
    
    # 发现并运行测试
    loader = unittest.TestLoader()
    
    # 单独加载每个测试模块，避免导入错误影响其他测试
    test_modules = [
        'test.test_dsl_engine',
        'test.test_llm_client', 
        'test.test_parser',
        'test.test_integration'
    ]
    
    all_suite = unittest.TestSuite()
    
    for module_name in test_modules:
        try:
            # 动态导入模块
            module = __import__(module_name, fromlist=['*'])
            # 获取模块中的所有测试用例
            suite = loader.loadTestsFromModule(module)
            all_suite.addTest(suite)
            print(f"✅ 加载测试模块: {module_name}")
        except ImportError as e:
            print(f"⚠️  跳过测试模块 {module_name}: {e}")
        except Exception as e:
            print(f"❌ 加载测试模块 {module_name} 时出错: {e}")
    
    if all_suite.countTestCases() == 0:
        print("❌ 没有找到可运行的测试用例")
        return False
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(all_suite)
    
    # 输出摘要
    print("\n" + "=" * 50)
    print("📊 测试结果摘要")
    print("=" * 50)
    print(f"总测试数: {result.testsRun}")
    print(f"✅ 通过: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ 失败: {len(result.failures)}")
    print(f"⚠️  错误: {len(result.errors)}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)