#!/usr/bin/env python3
"""
main.py - 简单DSL客服机器人 - 主程序
流程图：用户输入 → 主程序 → LLM意图识别 → DSL脚本引擎 → 生成回复 → 用户输出
"""

import os
import argparse
from dsl_engine import DSLEngine

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='DSL客服机器人')
    parser.add_argument('-d', '--debug', action='store_true',
                       help='启用调试模式')
    return parser.parse_args()

def main():
    """主程序入口"""
    # 解析命令行参数
    args = parse_arguments()
    
    # 优先级：命令行参数 > 环境变量
    debug_flag = args.debug or (os.environ.get('DSL_AGENT_DEBUG', 'false').lower() == 'true')
    
    if debug_flag:
        print("[DEBUG] 调试模式已启用")

    # 初始化DSL引擎（加载脚本文件）
    # 确保script.dsl文件存在于正确的位置
    script_path = os.path.join(os.path.dirname(__file__), "script.dsl")
    if not os.path.exists(script_path):
        raise FileNotFoundError(f"脚本文件未找到: {script_path}")
    
    dsl_engine = DSLEngine(script_path, debug=debug_flag)
    dsl_engine.start("greeting", "")

if __name__ == "__main__":
    main()