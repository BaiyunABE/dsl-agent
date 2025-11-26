#!/usr/bin/env python3
"""
测试覆盖率配置
"""

import coverage
import unittest
import os
import sys

def run_tests_with_coverage():
    """运行测试并生成覆盖率报告"""
    
    # 初始化覆盖率统计
    cov = coverage.Coverage(
        source=['src'],
        omit=['*/test_*', '*/__pycache__/*'],
        config_file=True
    )
    
    cov.start()
    
    try:
        # 运行测试
        from test_runner import TestRunner
        runner = TestRunner(verbose=True)
        success = runner.run_all_tests()
        
    finally:
        cov.stop()
        cov.save()
        
        # 生成报告
        print("\n📊 生成覆盖率报告...")
        cov.report()
        
        # 生成HTML报告
        cov.html_report(directory='htmlcov')
        print("📁 HTML报告已生成到 htmlcov/ 目录")
    
    return success

if __name__ == "__main__":
    success = run_tests_with_coverage()
    sys.exit(0 if success else 1)