"""
LLM客户端测试桩
"""
from unittest.mock import Mock

class MockLLMClient:
    def __init__(self, api_key=None, debug=False):
        self.debug = debug
        self.client = Mock()
        self.latest_intent = "unknown"
        self.mock_responses = {
            "greeting": "greeting",
            "help": "help", 
            "thanks": "thanks",
            "farewell": "farewell"
        }
    
    def recognize_intent(self, user_input, available_intents, latest_responses=None):
        if self.debug:
            print(f"[MOCK] 识别意图: '{user_input}' -> 可用意图: {available_intents}")
        
        # 简单的关键词匹配
        user_input_lower = user_input.lower()
        
        if "你好" in user_input_lower or "hello" in user_input_lower:
            return "greeting"
        elif "帮助" in user_input_lower or "help" in user_input_lower:
            return "help"
        elif "谢谢" in user_input_lower or "thank" in user_input_lower:
            return "thanks"
        elif "再见" in user_input_lower or "bye" in user_input_lower:
            return "farewell"
        else:
            return "unknown"
    
    def set_mock_response(self, intent, response):
        self.mock_responses[intent] = response