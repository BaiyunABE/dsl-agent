#!/usr/bin/env python3
"""
测试运行脚本 - 一键运行所有测试并生成报告
"""
import os
import sys
import subprocess
import datetime
from pathlib import Path

def run_tests():
    """运行所有测试并生成报告"""
    print("🚀 开始运行DSL客服机器人测试套件...")
    
    # 确保在正确的目录中运行
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # 创建测试报告目录
    reports_dir = script_dir / "test_reports"
    reports_dir.mkdir(exist_ok=True)
    
    # 生成时间戳
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = reports_dir / f"test_report_{timestamp}.html"
    
    # 基础测试命令
    test_cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "-v",
        f"--html={report_file}",
        "--tb=short"
    ]
    
    try:
        print("📊 运行测试...")
        result = subprocess.run(test_cmd, check=False, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 所有测试通过！")
        else:
            print("❌ 部分测试失败")
        
        print(f"📋 测试报告: {report_file}")
        
        # 显示测试结果摘要
        if result.stdout:
            for line in result.stdout.split('\n'):
                if 'passed' in line and ('failed' in line or 'error' in line):
                    print(f"📊 {line.strip()}")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ 测试运行异常: {e}")
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)