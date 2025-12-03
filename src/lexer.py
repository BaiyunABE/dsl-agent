'''
lexer.py -
DSL词法分析器模块，使用PLY实现词法分析，将DSL脚本分解为标记流。
'''

import ply.lex as lex

class Lexer:
    def __init__(self):
        self.lexer = None
        self.build()
    
    # 定义token名称
    tokens = (
        # 区块关键字
        'STEP',
        
        # 动作关键字
        'REPLY', 'LOG', 'WAIT',
        
        # 运算符和分隔符
        'PLUS',
        
        # 字面量
        'STRING', 'VARIABLE',
    )
    
    # 保留关键字映射
    reserved = {
        'step': 'STEP',
        'reply': 'REPLY', 
        'log': 'LOG',
        'wait': 'WAIT',
    }
    
    # 所有token的正则表达式规则
    t_PLUS = r'\+'
    
    # 处理标识符（包括关键字）
    def t_ID(self, t):
        r'[a-zA-Z_][a-zA-Z_0-9]*'
        # 检查是否是保留字
        t.type = self.reserved.get(t.value, 'ID')
        return t
    
    # 字符串字面量
    def t_STRING(self, t):
        r'\"([^\"\\]|\\.)*\"'
        t.value = t.value[1:-1]  # 去掉引号
        return t
    
    # 变量
    def t_VARIABLE(self, t):
        r'\$[a-zA-Z_][a-zA-Z0-9_]*'
        return t
    
    # 注释
    def t_COMMENT(self, t):
        r'\#.*'
        pass  # 忽略注释
    
    # 跟踪行号
    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)
    
    # 忽略空白字符
    t_ignore = ' \t'
    
    # 错误处理
    def t_error(self, t):
        print(f"非法字符: '{t.value[0]}' at line {t.lexer.lineno}")
        t.lexer.skip(1)
    
    def build(self, **kwargs):
        self.lexer = lex.lex(module=self, **kwargs)
    
    def tokenize(self, data):
        self.lexer.input(data)
        tokens = []
        while True:
            tok = self.lexer.token()
            if not tok:
                break
            tokens.append(tok)
        return tokens