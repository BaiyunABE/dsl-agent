#!/usr/bin/env python3
"""
测试桩文件
"""

class MockLLMClient:
    """模拟LLM客户端"""
    def recognize_intent(self, user_input, available_intents):
        return 'greeting'  # 总是返回问候意图

class MockParser:
    """模拟语法分析器"""
    def parse(self, content):
        return {'type': 'Script', 'children': []}

class MockCSVData:
    """模拟CSV数据"""
    def get_order_info(self, order_id):
        return {'发货时间': '2024-01-01'}

class MockFileSystem:
    """模拟文件系统"""
    def __init__(self):
        self.files = {}
    
    def read_file(self, path):
        return self.files.get(path, "")
    
    def write_file(self, path, content):
        self.files[path] = content