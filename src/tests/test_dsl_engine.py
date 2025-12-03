"""
DSL引擎测试用例
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from unittest.mock import patch, MagicMock
from dsl_engine import DSLEngine

class TestDSLEngine:
    def setup_method(self):
        self.test_script = '''
        step greeting
            reply "Hello! How can I help you?"
            log "User entered greeting step"
        
        step help
            reply "I can help with: 1. Product 2. Support"
            wait "product", "support"
        
        step thanks
            reply "You're welcome!"
        '''
    
    @patch('dsl_engine.LLMClient')
    @patch('parser.Parser')  # 正确路径：parser模块中的Parser类
    def test_engine_initialization(self, mock_parser, mock_llm):
        """测试引擎初始化"""
        mock_parser_instance = MagicMock()
        mock_parser.return_value = mock_parser_instance
        mock_parser_instance.parse.return_value = {'type': 'Script', 'children': []}
        
        # 模拟LLMClient
        mock_llm_instance = MagicMock()
        mock_llm.return_value = mock_llm_instance
        
        engine = DSLEngine(script_content=self.test_script, debug=False)
        
        assert engine.ast is not None
        assert 'user_input' in engine.variables
        assert engine.input_history == []
    
    @patch('dsl_engine.LLMClient')
    @patch('parser.Parser')  # 正确路径
    def test_evaluate_expression(self, mock_parser, mock_llm):
        """测试表达式求值"""
        mock_parser_instance = MagicMock()
        mock_parser.return_value = mock_parser_instance
        mock_parser_instance.parse.return_value = {'type': 'Script', 'children': []}
        
        engine = DSLEngine(script_content=self.test_script, debug=False)
        
        # 测试字符串求值
        string_node = {'type': 'String', 'value': 'test'}
        result = engine._evaluate_expression(string_node)
        assert result == 'test'
        
        # 测试变量求值
        engine.variables['test_var'] = 'variable_value'
        var_node = {'type': 'Variable', 'value': '$test_var'}
        result = engine._evaluate_expression(var_node)
        assert result == 'variable_value'
        
        # 测试算术表达式求值
        arithmetic_node = {
            'type': 'Arithmetic',
            'value': '+',
            'children': [
                {'type': 'String', 'value': 'hello'},
                {'type': 'String', 'value': ' world'}
            ]
        }
        result = engine._evaluate_expression(arithmetic_node)
        assert result == 'hello world'
    
    @patch('dsl_engine.LLMClient')
    @patch('parser.Parser')  # 正确路径
    def test_execute_reply_statement(self, mock_parser, mock_llm):
        """测试执行reply语句"""
        mock_parser_instance = MagicMock()
        mock_parser.return_value = mock_parser_instance
        
        # 创建模拟的AST
        ast = {
            'type': 'Script',
            'children': [
                {
                    'type': 'Step',
                    'value': 'greeting',
                    'children': [
                        {
                            'type': 'Reply',
                            'value': {'type': 'String', 'value': 'Hello!'}
                        }
                    ]
                }
            ]
        }
        mock_parser_instance.parse.return_value = ast
        
        engine = DSLEngine(script_content=self.test_script, debug=False)
        engine.ast = ast
        
        # 测试reply语句执行
        reply_stmt = ast['children'][0]['children'][0]
        responses = engine._execute_statement(reply_stmt, 'test input')
        
        assert len(responses) == 1
        assert responses[0] == 'Hello!'
    
    @patch('dsl_engine.LLMClient')
    @patch('parser.Parser')  # 正确路径
    def test_process_step(self, mock_parser, mock_llm):
        """测试处理步骤"""
        mock_parser_instance = MagicMock()
        mock_parser.return_value = mock_parser_instance
        
        # 创建模拟的AST
        ast = {
            'type': 'Script',
            'children': [
                {
                    'type': 'Step',
                    'value': 'greeting',
                    'children': [
                        {
                            'type': 'Reply',
                            'value': {'type': 'String', 'value': 'Welcome!'}
                        }
                    ]
                }
            ]
        }
        mock_parser_instance.parse.return_value = ast
        
        engine = DSLEngine(script_content=self.test_script, debug=False)
        engine.ast = ast
        
        response = engine.process('greeting', 'test input')
        assert response == 'Welcome!'
        assert engine.current_step == 'greeting'
    
    @patch('dsl_engine.LLMClient')
    @patch('parser.Parser')  # 正确路径
    def test_get_steps(self, mock_parser, mock_llm):
        """测试获取步骤列表"""
        mock_parser_instance = MagicMock()
        mock_parser.return_value = mock_parser_instance
        
        ast = {
            'type': 'Script',
            'children': [
                {'type': 'Step', 'value': 'greeting'},
                {'type': 'Step', 'value': 'help'},
                {'type': 'Step', 'value': 'thanks'}
            ]
        }
        mock_parser_instance.parse.return_value = ast
        
        engine = DSLEngine(script_content=self.test_script, debug=False)
        engine.ast = ast
        
        steps = engine.get_steps()
        assert len(steps) == 3
        assert 'greeting' in steps
        assert 'help' in steps
        assert 'thanks' in steps
    
    @patch('dsl_engine.LLMClient')
    @patch('parser.Parser')  # 正确路径
    def test_variables_management(self, mock_parser, mock_llm):
        """测试变量管理"""
        mock_parser_instance = MagicMock()
        mock_parser.return_value = mock_parser_instance
        mock_parser_instance.parse.return_value = {'type': 'Script', 'children': []}
        
        engine = DSLEngine(script_content=self.test_script, debug=False)
        
        # 测试用户输入变量更新
        engine._execute_statement({'type': 'Reply', 'value': {'type': 'String', 'value': 'test'}}, 'user input')
        assert engine.variables['user_input'] == 'user input'
        assert len(engine.variables['input_history']) == 1
        
        # 测试获取变量状态
        variables = engine.get_variables()
        assert 'user_input' in variables
        assert variables['user_input'] == 'user input'