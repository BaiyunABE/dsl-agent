#!/usr/bin/env python3
"""
测试驱动框架 - 主测试运行器
"""

import unittest
import sys
import os
import time
from typing import List, Dict, Any

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 现在导入测试模块
try:
    from test.test_dsl_engine import TestDSLEngine
    from test.test_llm_client import TestLLMClient
    from test.test_parser import TestParser
    from test.test_integration import TestIntegration
    from test.test_stubs import MockLLMClient, MockParser, MockCSVData, MockFileSystem
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保测试文件在正确的目录结构中")
    sys.exit(1)

class TestRunner:
    """测试运行器"""
    
    def __init__(self, verbose=True):
        self.verbose = verbose
        self.test_results = {}
        self.start_time = None
        self.end_time = None
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始运行DSL客服机器人测试套件")
        print("=" * 60)
        
        self.start_time = time.time()
        
        # 创建测试套件
        test_suite = unittest.TestSuite()
        
        # 添加各个测试模块
        test_modules = [
            TestDSLEngine,
            TestLLMClient,
            TestParser,
            TestIntegration
        ]
        
        for test_module in test_modules:
            try:
                suite = unittest.TestLoader().loadTestsFromTestCase(test_module)
                test_suite.addTest(suite)
                print(f"✅ 加载测试模块: {test_module.__name__}")
            except Exception as e:
                print(f"❌ 加载测试模块失败 {test_module.__name__}: {e}")
        
        # 运行测试
        runner = unittest.TextTestRunner(verbosity=2 if self.verbose else 1)
        result = runner.run(test_suite)
        
        self.end_time = time.time()
        
        # 输出测试结果摘要
        self._print_summary(result)
        
        return result.wasSuccessful()
    
    def _print_summary(self, result):
        """打印测试结果摘要"""
        print("\n" + "=" * 60)
        print("📊 测试结果摘要")
        print("=" * 60)
        
        total_tests = result.testsRun
        failed_tests = len(result.failures)
        errored_tests = len(result.errors)
        passed_tests = total_tests - failed_tests - errored_tests
        
        print(f"总测试数: {total_tests}")
        print(f"✅ 通过: {passed_tests}")
        print(f"❌ 失败: {failed_tests}")
        print(f"⚠️  错误: {errored_tests}")
        print(f"⏱️  耗时: {self.end_time - self.start_time:.2f}秒")
        
        # 显示失败的测试
        if result.failures:
            print("\n❌ 失败的测试:")
            for test, traceback in result.failures:
                print(f"  - {test}")
        
        if result.errors:
            print("\n⚠️  错误的测试:")
            for test, traceback in result.errors:
                print(f"  - {test}")

def run_performance_tests():
    """运行性能测试"""
    print("\n🎯 性能测试")
    print("=" * 40)
    
    import time
    try:
        from src.dsl_engine import DSLEngine
        
        # 性能测试配置
        test_cases = [
            ("简单问候", "greeting", ""),
            ("订单查询", "provide_order_number", "ORDER123"),
            ("发货时间", "ask_delivery_time", "")
        ]
        
        # 预热
        engine = DSLEngine("src/script.dsl", debug=False)
        engine.process("greeting")
        
        # 性能测试
        for test_name, intent, user_input in test_cases:
            start_time = time.time()
            
            # 执行100次
            for i in range(100):
                response = engine.process(intent, user_input)
            
            end_time = time.time()
            avg_time = (end_time - start_time) * 1000 / 100  # 平均毫秒
            
            print(f"{test_name}: {avg_time:.2f}ms/次")
    except ImportError as e:
        print(f"性能测试跳过: {e}")

def main():
    """主函数"""
    # 运行单元测试
    runner = TestRunner(verbose=True)
    success = runner.run_all_tests()
    
    # 运行性能测试（如果单元测试通过）
    if success:
        run_performance_tests()
    
    # 返回退出码
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()