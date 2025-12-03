"""
词法分析器测试用例
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from lexer import Lexer

class TestLexer:
    def setup_method(self):
        self.lexer = Lexer()
    
    def test_tokenize_basic(self):
        """测试基本token识别"""
        tokens = self.lexer.tokenize('step greeting')
        token_types = [t.type for t in tokens]
        # 'greeting' 是标识符，应该是 'ID'
        assert token_types == ['STEP', 'ID']
    
    def test_tokenize_string(self):
        """测试字符串token"""
        tokens = self.lexer.tokenize('"这是一个字符串"')
        assert len(tokens) == 1
        assert tokens[0].type == 'STRING'
        assert tokens[0].value == '这是一个字符串'
    
    def test_tokenize_variable(self):
        """测试变量token"""
        tokens = self.lexer.tokenize('$user_input')
        assert len(tokens) == 1
        assert tokens[0].type == 'VARIABLE'
        assert tokens[0].value == '$user_input'
    
    def test_tokenize_arithmetic(self):
        """测试算术运算符"""
        tokens = self.lexer.tokenize('a + b')
        token_types = [t.type for t in tokens]
        # 'a' 和 'b' 是标识符，应该是 'ID'
        assert token_types == ['ID', 'PLUS', 'ID']
    
    def test_tokenize_complex_script(self):
        """测试复杂脚本token化"""
        script = '''
        step greeting
            reply "Hello " + $name
            log "User greeted"
        '''
        tokens = self.lexer.tokenize(script)
        token_types = [t.type for t in tokens]
        
        assert 'STEP' in token_types
        assert 'REPLY' in token_types
        assert 'LOG' in token_types
        assert 'PLUS' in token_types
        assert 'VARIABLE' in token_types
        assert 'STRING' in token_types
        assert 'ID' in token_types  # greeting 是 ID
    
    def test_ignore_comments(self):
        """测试注释忽略"""
        tokens = self.lexer.tokenize('step test # 这是一个注释')
        token_types = [t.type for t in tokens]
        # 'test' 是标识符，应该是 'ID'
        assert token_types == ['STEP', 'ID']
    
    def test_tokenize_keywords(self):
        """测试关键字识别"""
        tokens = self.lexer.tokenize('step reply log wait')
        token_types = [t.type for t in tokens]
        # 所有都应该是关键字类型
        assert token_types == ['STEP', 'REPLY', 'LOG', 'WAIT']