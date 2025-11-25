#!/usr/bin/env python3
"""
简单DSL客服机器人 - 主程序
流程图：用户输入 → 主程序 → LLM意图识别 → DSL脚本引擎 → 生成回复 → 用户输出
"""

import os
from llm_client import LLMClient
from dsl_engine import DSLEngine

def main():
    # 初始化各个模块
    print("=== 简单DSL客服机器人 ===")
    
    # 1. 初始化LLM客户端（连接大模型API）
    # 可通过环境变量 `DSL_DEBUG=1` 启用 LLMClient 的调试输出
    debug_flag = os.environ.get('DSL_DEBUG', '').lower() in ('1', 'true', 'yes')
    llm_client = LLMClient(debug=debug_flag)
    print("✅ LLM客户端已初始化")
    
    # 2. 初始化DSL引擎（加载脚本文件）
    dsl_engine = DSLEngine("script.dsl")
    print("✅ DSL引擎已初始化")
    print("可用意图:", dsl_engine.get_intents())
    print()
    
    # 3. 主对话循环
    print("开始对话吧！（输入'退出'结束）")
    while True:
        try:
            # 用户输入
            user_input = input("👤 用户: ").strip()
            
            if user_input in ['退出', 'quit', 'exit']:
                print("再见！")
                break
                
            if not user_input:
                continue
            
            # LLM意图识别
            intent = llm_client.recognize_intent(user_input, dsl_engine.get_intents())
            print(f"🔍 识别意图: {intent}")
            
            # DSL脚本引擎处理
            response = dsl_engine.process(intent, user_input)
            
            # 生成回复
            print(f"🤖 机器人: {response}")
            print()
            
        except KeyboardInterrupt:
            print("\n程序结束")
            break
        except Exception as e:
            print(f"❌ 错误: {e}")

if __name__ == "__main__":
    main()
