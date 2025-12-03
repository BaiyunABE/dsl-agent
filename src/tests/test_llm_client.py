"""
LLM客户端测试用例
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from unittest.mock import patch, MagicMock
from llm_client import LLMClient

class TestLLMClient:
    def setup_method(self):
        self.api_key = "test_api_key"
    
    @patch.dict('os.environ', {'DSL_AGENT_API_KEY': 'env_api_key'})
    def test_initialization_with_env_key(self):
        """测试使用环境变量API密钥初始化"""
        client = LLMClient(debug=False)
        assert client.api_key == 'env_api_key'
    
    def test_initialization_with_explicit_key(self):
        """测试使用显式API密钥初始化"""
        client = LLMClient(api_key=self.api_key, debug=False)
        assert client.api_key == self.api_key
    
    @patch('llm_client.OpenAI')
    def test_recognize_intent_success(self, mock_openai):
        """测试成功识别意图"""
        # 模拟API响应
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "greeting"
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        client = LLMClient(api_key=self.api_key, debug=False)
        client.client = mock_client
        
        intent = client.recognize_intent(
            "你好", 
            ["greeting", "help", "thanks"],
            ["上一个响应"]
        )
        
        assert intent == "greeting"
        mock_client.chat.completions.create.assert_called_once()
    
    @patch('llm_client.OpenAI')
    def test_recognize_intent_fallback(self, mock_openai):
        """测试意图识别失败时的回退"""
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_openai.return_value = mock_client
        
        client = LLMClient(api_key=self.api_key, debug=False)
        client.client = mock_client
        
        intent = client.recognize_intent("test", ["greeting", "help"], [])
        
        assert intent == "unknown"
    
    def test_mask_key(self):
        """测试API密钥掩码"""
        client = LLMClient(api_key="1234567890abcdef", debug=False)
        
        masked = client._mask_key("1234567890abcdef")
        assert masked == "1234...cdef"
        
        masked_short = client._mask_key("1234")
        assert masked_short == "**34"
        
        masked_empty = client._mask_key("")
        assert masked_empty == "(no-key)"