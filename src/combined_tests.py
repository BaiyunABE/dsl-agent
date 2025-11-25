#!/usr/bin/env python3
"""
合并测试文件：包含单元测试与端到端测试，供 pytest 收集或直接运行。
运行：
  pytest -q src/combined_tests.py
或：
  python src/combined_tests.py
"""

from dsl_engine import DSLEngine
import re


# ---------------------------
# 单元 / 功能测试（来自 test_dsl_engine.py）
# ---------------------------

def test_user_input_conditions():
    """测试用户输入相关的条件"""
    engine = DSLEngine("script.dsl")

    # 测试contains条件
    test_cases = [
        ("我叫张三", 'condition $user_input contains "我叫"', True),
        ("你好", 'condition $user_input contains "我叫"', False),
        ("我是李四", 'condition $user_input contains "我是"', True),
    ]

    for user_input, condition, expected in test_cases:
        result = engine._evaluate_condition(condition, user_input)
        assert result == expected, f"测试失败: {user_input} 条件: {condition} -> {result} (期望: {expected})"

    # 测试matches条件
    test_cases = [
        ("ORDER123", 'condition $user_input matches "ORDER\\\\d+"', True),
        ("order123", 'condition $user_input matches "ORDER\\\\d+"', False),
        ("ABC123", 'condition $user_input matches "ORDER\\\\d+"', False),
    ]

    for user_input, condition, expected in test_cases:
        result = engine._evaluate_condition(condition, user_input)
        assert result == expected, f"测试失败(matcher): {user_input} 条件: {condition} -> {result} (期望: {expected})"


def test_variable_conditions():
    """测试变量相关的条件"""
    engine = DSLEngine("script.dsl")

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
        assert result == expected, f"测试失败: {condition} -> {result} (期望: {expected})"


def test_extract_functionality():
    """测试信息提取功能"""
    engine = DSLEngine("script.dsl")

    # 测试姓名提取
    test_cases = [
        "我叫张三",
        "我是李四",
        "名字是王五",
        "不知道"
    ]

    for user_input in test_cases:
        response = engine.process("provide_name", user_input)
        # process may return None or a reply; just ensure engine.variables updated when pattern matches
        if re.search(r"我叫(.*)|我是(.*)", user_input):
            assert engine.variables.get('user_name') is not None, f"提取失败: {user_input}"


def test_template_processing():
    """测试模板处理（随机回复/时间/随机数）"""
    engine = DSLEngine("script.dsl")

    # 随机回复：只要不报错并返回字符串即通过
    resp = engine.process("thankyou", "谢谢")
    assert resp is not None, "thankyou 模板处理返回为空"

    # 人工客服随机数模板
    resp = engine.process("ask_human_agent", "转人工")
    assert resp is not None and isinstance(resp, str), "ask_human_agent 返回异常"


def test_complex_workflow():
    """测试完整工作流程的关键路径（模拟对话）"""
    engine = DSLEngine("script.dsl")

    # greeting -> ask name
    resp = engine.process('greeting', '你好')
    assert resp is not None, 'greeting 没有回复'

    # provide name
    resp = engine.process('provide_name', '我叫测试用户')
    assert resp is not None, 'provide_name 没有回复'

    # ask_time
    resp = engine.process('ask_time', '现在时间')
    assert resp is not None, 'ask_time 没有回复'

    # check_order: will ask for order when none
    engine.variables['last_order'] = ''
    resp = engine.process('check_order', '查询订单')
    assert resp is not None, 'check_order 没有回复'

    # provide_order_number valid
    resp = engine.process('provide_order_number', 'ORDER888888')
    assert engine.variables.get('last_order') == 'ORDER888888', 'last_order 未设置'


# ---------------------------
# 端到端测试（来自 test_dsl_engine_e2e.py）
# ---------------------------

def test_e2e_flow():
    """端到端对话流程测试"""
    engine = DSLEngine("script.dsl", debug=False)

    # 1) greeting -> should ask for name and set waiting_for to 'name'
    resp = engine.process('greeting', '你好')
    assert resp is not None and ('请问如何称呼您' in resp or '请问如何称呼您？' in resp), f"greeting reply missing: {resp}"
    assert engine.waiting_for == 'name', f"expected waiting_for 'name', got {engine.waiting_for}"

    # 2) provide_name with plain name (容错路径)
    resp = engine.process('provide_name', 'Abe')
    assert resp is not None and '很高兴认识您' in resp, f"provide_name reply bad: {resp}"
    assert engine.variables.get('user_name') == 'Abe', f"user_name not set: {engine.variables.get('user_name')}"

    # 3) ask_time -> should call get_time and set current_time
    resp = engine.process('ask_time', '现在时间')
    assert resp is not None and ('当前时间是' in resp or '今天是' in resp), f"ask_time reply unexpected: {resp}"
    assert engine.variables.get('current_time') is not None, "current_time not set"

    # 4) check_order when no last_order set -> should ask for order number and set waiting_for
    engine.variables['last_order'] = ''
    resp = engine.process('check_order', '我想查订单')
    assert resp is not None and ('请问您要查询哪个订单号' in resp or '请问您要查询哪个订单号？' in resp), f"check_order prompt unexpected: {resp}"
    assert engine.waiting_for == 'order_number', f"expected waiting_for 'order_number', got {engine.waiting_for}"

    # 5) provide valid order number
    resp = engine.process('provide_order_number', 'ORDER123')
    assert engine.variables.get('last_order') == 'ORDER123', f"last_order not set: {engine.variables.get('last_order')}"
    assert resp is not None and ('验证成功' in resp or '已发货' in resp), f"provide_order_number valid failed: {resp}"

    # 6) provide invalid order number
    resp = engine.process('provide_order_number', 'BAD123')
    assert resp is not None and ('格式不正确' in resp or '无效' in resp), f"provide_order_number invalid handling failed: {resp}"


# 允许直接运行该文件以查看控制台输出
def _run_all_e2e():
    print('Running combined E2E sequence...')
    engine = DSLEngine("script.dsl", debug=False)
    print('Loaded intents:', engine.get_intents())

    resp = engine.process('greeting', '你好')
    print('greeting ->', resp)
    resp = engine.process('provide_name', 'Abe')
    print('provide_name ->', resp)
    resp = engine.process('ask_time', '现在时间')
    print('ask_time ->', resp)
    engine.variables['last_order'] = ''
    resp = engine.process('check_order', '我想查订单')
    print('check_order ->', resp)
    resp = engine.process('provide_order_number', 'ORDER123')
    print('provide_order_number ->', resp)
    resp = engine.process('provide_order_number', 'BAD123')
    print('provide_order_number (bad) ->', resp)


if __name__ == '__main__':
    # 当直接执行时，运行 e2e 序列，便于手动验证
    _run_all_e2e()
