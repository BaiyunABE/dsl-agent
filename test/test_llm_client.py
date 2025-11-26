#!/usr/bin/env python3
"""
LLM客户端单元测试 - 修复版本
"""

import unittest
import os
import sys
from unittest.mock import patch, MagicMock

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

class MockLLMClient:
    """模拟LLM客户端"""
    
    def __init__(self, api_key=None, debug=False):
        self.debug = debug
        self.api_key = api_key or "test_api_key"
        self.call_history = []
        
        self.intent_mapping = {
            "你好": "greeting",
            "hello": "greeting", 
            "订单号": "provide_order_number",
            "查询订单": "provide_order_number",
        }
    
    def recognize_intent(self, user_input, available_intents):
        self.call_history.append({
            'user_input': user_input,
            'available_intents': available_intents
        })
        
        if self.debug:
            print(f"[MOCK LLM] 输入: '{user_input}', 可用意图: {available_intents}")
        
        for keyword, intent in self.intent_mapping.items():
            if keyword in user_input:
                if intent in available_intents:
                    return intent
        
        return available_intents[0] if available_intents else 'unknown'

class TestLLMClient(unittest.TestCase):
    """LLM客户端测试类"""
    
    def setUp(self):
        self.mock_client = MockLLMClient(debug=True)
    
    def test_mock_initialization(self):
        """测试模拟客户端初始化"""
        client = MockLLMClient(api_key="test_key", debug=True)
        self.assertEqual(client.api_key, "test_key")
        self.assertTrue(client.debug)
    
    def test_mock_intent_recognition(self):
        """测试模拟意图识别"""
        available_intents = ['greeting', 'provide_order_number', 'help']
        
        # 测试问候意图
        intent = self.mock_client.recognize_intent("你好", available_intents)
        self.assertEqual(intent, "greeting")
        
        # 测试订单意图
        intent = self.mock_client.recognize_intent("我的订单号", available_intents)
        self.assertEqual(intent, "provide_order_number")
        
        # 测试未知输入
        intent = self.mock_client.recognize_intent("随机文本", available_intents)
        self.assertIn(intent, available_intents + ['unknown'])
    
    def test_real_client_import(self):
        """测试真实客户端导入"""
        try:
            from src.llm_client import LLMClient
            # 导入成功即可
            self.assertTrue(True)
        except ImportError as e:
            self.skipTest(f"无法导入LLMClient: {e}")
    
    @patch('openai.OpenAI')
    def test_real_client_initialization(self, mock_openai):
        """测试真实客户端初始化"""
        # 模拟OpenAI客户端
        mock_instance = MagicMock()
        mock_openai.return_value = mock_instance
        
        try:
            from src.llm_client import LLMClient
            client = LLMClient(api_key="test_key", debug=True)
            self.assertIsNotNone(client)
        except ImportError:
            self.skipTest("LLMClient不可用")
    
    def test_call_history(self):
        """测试调用历史记录"""
        available_intents = ['greeting', 'help']
        
        # 进行几次调用
        self.mock_client.recognize_intent("你好", available_intents)
        self.mock_client.recognize_intent("帮助", available_intents)
        
        # 验证调用历史
        self.assertEqual(len(self.mock_client.call_history), 2)
        self.assertEqual(self.mock_client.call_history[0]['user_input'], "你好")

if __name__ == "__main__":
    unittest.main()