#!/usr/bin/env python3
"""
综合测试运行器 - 包含详细报告
"""

import sys
import os
import unittest
import time

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

def check_environment():
    """检查测试环境"""
    print("🔍 检查测试环境...")
    
    required_dirs = ['src', 'test']
    required_files = [
        'src/dsl_engine.py',
        'src/llm_client.py',
        'src/parser.py',
        'src/main.py',
        'test/test_dsl_engine.py',
        'test/test_llm_client.py',
        'test/test_parser.py',
        'test/test_integration.py'
    ]
    
    # 检查目录
    for dir_name in required_dirs:
        if not os.path.exists(dir_name):
            print(f"❌ 缺少目录: {dir_name}")
            return False
        else:
            print(f"✅ 目录存在: {dir_name}")
    
    # 检查文件
    for file_path in required_files:
        if not os.path.exists(file_path):
            print(f"❌ 缺少文件: {file_path}")
            return False
        else:
            print(f"✅ 文件存在: {file_path}")
    
    print("✅ 环境检查通过")
    return True

def run_module_tests():
    """运行模块级别的测试"""
    print("\n🧪 运行模块测试...")
    
    test_modules = {
        'DSL引擎': 'test.test_dsl_engine',
        'LLM客户端': 'test.test_llm_client', 
        '语法分析器': 'test.test_parser',
        '集成测试': 'test.test_integration'
    }
    
    results = {}
    loader = unittest.TestLoader()
    
    for module_name, module_path in test_modules.items():
        try:
            print(f"\n📦 测试模块: {module_name}")
            module = __import__(module_path, fromlist=['*'])
            suite = loader.loadTestsFromModule(module)
            
            runner = unittest.TextTestRunner(verbosity=1, stream=sys.stderr)
            result = runner.run(suite)
            
            results[module_name] = {
                'tests_run': result.testsRun,
                'failures': len(result.failures),
                'errors': len(result.errors),
                'success': result.wasSuccessful()
            }
            
            status = "✅ 通过" if result.wasSuccessful() else "❌ 失败"
            print(f"   {status} - 测试数: {result.testsRun}, 失败: {len(result.failures)}, 错误: {len(result.errors)}")
            
        except Exception as e:
            print(f"❌ 测试模块 {module_name} 时出错: {e}")
            results[module_name] = {'error': str(e)}
    
    return results

def generate_report(results, duration):
    """生成测试报告"""
    print("\n" + "="*60)
    print("📊 详细测试报告")
    print("="*60)
    
    total_tests = 0
    total_failures = 0
    total_errors = 0
    passed_modules = 0
    
    for module_name, result in results.items():
        if 'error' in result:
            print(f"\n❌ {module_name}: 错误 - {result['error']}")
            continue
        
        tests_run = result['tests_run']
        failures = result['failures']
        errors = result['errors']
        success = result['success']
        
        total_tests += tests_run
        total_failures += failures
        total_errors += errors
        
        if success:
            passed_modules += 1
            status = "✅ 通过"
        else:
            status = "❌ 失败"
        
        print(f"\n{status} {module_name}:")
        print(f"   测试用例: {tests_run}")
        print(f"   失败: {failures}")
        print(f"   错误: {errors}")
    
    print("\n" + "="*40)
    print("📈 总体统计")
    print("="*40)
    print(f"总测试模块: {len(results)}")
    print(f"通过模块: {passed_modules}")
    print(f"总测试用例: {total_tests}")
    print(f"总失败数: {total_failures}")
    print(f"总错误数: {total_errors}")
    print(f"测试耗时: {duration:.2f}秒")
    
    success_rate = (passed_modules / len(results)) * 100 if results else 0
    print(f"成功率: {success_rate:.1f}%")
    
    return passed_modules == len(results)

def main():
    """主函数"""
    print("🚀 DSL客服机器人综合测试套件")
    print("="*50)
    
    # 检查环境
    if not check_environment():
        print("❌ 环境检查失败，无法继续测试")
        sys.exit(1)
    
    # 运行测试
    start_time = time.time()
    results = run_module_tests()
    end_time = time.time()
    
    duration = end_time - start_time
    
    # 生成报告
    all_passed = generate_report(results, duration)
    
    # 最终结果
    print("\n" + "="*50)
    if all_passed:
        print("🎉 所有测试通过！")
        print("✅ 系统准备就绪")
    else:
        print("⚠️  部分测试失败")
        print("💡 请检查失败的测试用例")
    
    print("="*50)
    
    sys.exit(0 if all_passed else 1)

if __name__ == "__main__":
    main()