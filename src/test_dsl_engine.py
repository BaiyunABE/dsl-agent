#!/usr/bin/env python3
"""
DSL引擎最终修复测试
"""

from dsl_engine import DSLEngine
import re


def test_user_input_conditions():
    """测试用户输入相关的条件"""
    print("=== 测试用户输入条件 ===")

    engine = DSLEngine("enhanced_script.dsl")

    # 测试contains条件
    print("--- 测试contains条件 ---")
    test_cases = [
        ("我叫张三", "condition $user_input contains \"我叫\"", True),
        ("你好", "condition $user_input contains \"我叫\"", False),
        ("我是李四", "condition $user_input contains \"我是\"", True),
    ]

    for user_input, condition, expected in test_cases:
        result = engine._evaluate_condition(condition, user_input)
        print(f"输入: '{user_input}', 条件: {condition} -> {result} (期望: {expected})")
        assert result == expected, f"测试失败: {user_input}"

    # 测试matches条件
    print("\n--- 测试matches条件 ---")
    test_cases = [
        ("ORDER123", "condition $user_input matches \"ORDER\\\\d+\"", True),
        ("order123", "condition $user_input matches \"ORDER\\\\d+\"", False),
        ("ABC123", "condition $user_input matches \"ORDER\\\\d+\"", False),
    ]

    for user_input, condition, expected in test_cases:
        result = engine._evaluate_condition(condition, user_input)
        print(f"输入: '{user_input}', 条件: {condition} -> {result} (期望: {expected})")


def test_variable_conditions():
    """测试变量相关的条件"""
    print("\n=== 测试变量条件 ===")

    engine = DSLEngine("enhanced_script.dsl")

    # 测试变量比较
    print("--- 测试变量比较 ---")
    engine.variables['login_count'] = 0
    engine.variables['last_order'] = "ORDER123"

    test_cases = [
        ("$login_count == 0", True),
        ("$login_count != 0", False),
        ("$last_order != \"\"", True),
        ("$last_order == \"\"", False),
    ]

    for condition, expected in test_cases:
        result = engine._evaluate_condition(condition, "")
        print(f"条件: {condition} -> {result} (期望: {expected})")
        assert result == expected, f"测试失败: {condition}"


def test_complex_workflow():
    """测试完整工作流程"""
    print("\n=== 测试完整工作流程 ===")

    engine = DSLEngine("enhanced_script.dsl")

    # 模拟真实对话流程
    conversations = [
        ("greeting", "你好"),
        ("provide_name", "我叫测试用户"),
        ("check_order", "查询订单"),
        ("provide_order_number", "ORDER888888"),
        ("return_request", "我要退货"),
        ("confirm_return", "确认退货"),
        ("thankyou", "谢谢")
    ]

    for i, (intent, user_input) in enumerate(conversations):
        print(f"\n步骤 {i + 1}: {intent}")
        print(f"👤 用户: {user_input}")

        response = engine.process(intent, user_input)
        print(f"🤖 机器人: {response}")

        # 显示关键变量状态
        key_vars = ['user_name', 'login_count', 'last_order']
        var_status = {k: engine.variables.get(k, '未设置') for k in key_vars}
        print(f"📊 变量状态: {var_status}")
        print(f"⏳ 等待状态: {engine.get_waiting_status()}")


def test_extract_functionality():
    """测试信息提取功能"""
    print("\n=== 测试信息提取 ===")

    engine = DSLEngine("enhanced_script.dsl")

    # 测试姓名提取
    test_cases = [
        "我叫张三",
        "我是李四",
        "名字是王五",
        "不知道"
    ]

    for user_input in test_cases:
        print(f"\n输入: {user_input}")
        response = engine.process("provide_name", user_input)
        print(f"回复: {response}")
        print(f"提取的用户名: {engine.variables.get('user_name', '未提取')}")


def test_template_processing():
    """测试模板处理"""
    print("\n=== 测试模板处理 ===")

    engine = DSLEngine("enhanced_script.dsl")

    # 测试随机回复
    print("--- 测试随机回复 ---")
    for i in range(3):
        response = engine.process("thankyou", "谢谢")
        first_line = response.split('\n')[0] if response else "无回复"
        print(f"随机回复 {i + 1}: {first_line}")

    # 测试动态内容
    print("\n--- 测试动态内容 ---")
    response = engine.process("ask_human_agent", "转人工")
    print(f"人工客服回复: {response}")


if __name__ == "__main__":
    print("🎯 DSL引擎最终测试")
    print("=" * 60)

    try:
        test_user_input_conditions()
        test_variable_conditions()
        test_extract_functionality()
        test_template_processing()
        test_complex_workflow()

        print("\n" + "=" * 60)
        print("✅ 所有测试完成！DSL引擎功能正常")

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback

        traceback.print_exc()
        