#!/usr/bin/env python3
"""
简单的端到端测试脚本（DSL 引擎）

用途：快速验证常见对话流（问候 -> 提供姓名 -> 查询时间 -> 订单流程）。
运行方式（仓库根目录，在 PowerShell 下）：
  python .\src\test_dsl_engine_e2e.py

注意：该测试直接使用 `DSLEngine`，不依赖 LLM 服务（使用内置/脚本逻辑）。
"""

from dsl_engine import DSLEngine


def run_tests():
    engine = DSLEngine("script.dsl", debug=False)
    print("Loaded intents:", engine.get_intents())

    # 1) greeting -> should ask for name and set waiting_for to 'name'
    resp = engine.process('greeting', '你好')
    assert resp is not None and '请问如何称呼您' in resp, f"greeting reply missing: {resp}"
    assert engine.waiting_for == 'name', f"expected waiting_for 'name', got {engine.waiting_for}"
    print("[OK] greeting -> asked for name")

    # 2) provide_name with plain name (容错路径)
    resp = engine.process('provide_name', 'Abe')
    assert resp is not None and '很高兴认识您' in resp, f"provide_name reply bad: {resp}"
    assert engine.variables.get('user_name') == 'Abe', f"user_name not set: {engine.variables.get('user_name')}"
    print("[OK] provide_name -> name captured as 'Abe'")

    # 3) ask_time -> should call get_time and set current_time
    resp = engine.process('ask_time', '现在时间')
    assert resp is not None and ('当前时间是' in resp or '今天是' in resp), f"ask_time reply unexpected: {resp}"
    assert engine.variables.get('current_time') is not None, "current_time not set"
    print("[OK] ask_time -> current_time set")

    # 4) check_order when no last_order set -> should ask for order number and set waiting_for
    engine.variables['last_order'] = ''
    resp = engine.process('check_order', '我想查订单')
    assert resp is not None and ('请问您要查询哪个订单号' in resp or '请问您要查询哪个订单号？' in resp), f"check_order prompt unexpected: {resp}"
    assert engine.waiting_for == 'order_number', f"expected waiting_for 'order_number', got {engine.waiting_for}"
    print("[OK] check_order -> asked for order number")

    # 5) provide valid order number
    resp = engine.process('provide_order_number', 'ORDER123')
    # engine should store last_order and validate it
    assert engine.variables.get('last_order') == 'ORDER123', f"last_order not set: {engine.variables.get('last_order')}"
    assert resp is not None and ('验证成功' in resp or '已发货' in resp), f"provide_order_number valid failed: {resp}"
    print("[OK] provide_order_number -> valid order handled")

    # 6) provide invalid order number
    resp = engine.process('provide_order_number', 'BAD123')
    assert resp is not None and ('格式不正确' in resp or '无效' in resp), f"provide_order_number invalid handling failed: {resp}"
    print("[OK] provide_order_number -> invalid order handled")

    print('\n✅ All E2E tests passed.')


if __name__ == '__main__':
    run_tests()
