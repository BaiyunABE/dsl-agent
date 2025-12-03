"""
parser.py -
DSL解析器模块，使用PLY实现词法分析和语法分析，将DSL脚本解析为字典格式的语法树。
"""

import ply.yacc as yacc
from lexer import Lexer

class Parser:
    def __init__(self, debug=False):
        self.lexer = Lexer()
        self.tokens = self.lexer.tokens
        self.parser = yacc.yacc(module=self, debug=debug, write_tables=False)
        self.ast = None
    
    def create_node(self, node_type, children=None, value=None, lineno=None):
        """创建字典格式的语法树节点"""
        node = {'type': node_type}
        if value is not None:
            node['value'] = value
        if lineno is not None:
            node['lineno'] = lineno
        if children is not None:
            node['children'] = children
        return node
    
    # 语法规则
    def p_script(self, p):
        '''script : sections'''
        p[0] = self.create_node('Script', p[1], lineno=1)
        self.ast = p[0]
    
    def p_sections(self, p):
        '''sections : section sections
                    | section'''
        if len(p) == 3:
            p[0] = [p[1]] + p[2]
        else:
            p[0] = [p[1]]
    
    def p_section(self, p):
        '''section : step_section'''
        p[0] = p[1]
    
    # Step 区块
    def p_step_section(self, p):
        'step_section : STEP ID statements'  # 修改：使用ID而不是STRING
        p[0] = self.create_node('Step', p[3], p[2], p.lineno(1))
    
    # 语句
    def p_statements(self, p):
        '''statements : statement statements
                     | statement'''
        if len(p) == 3:
            p[0] = [p[1]] + p[2]
        else:
            p[0] = [p[1]]
    
    def p_statement(self, p):
        '''statement : reply_statement
                    | log_statement
                    | wait_statement'''
        p[0] = p[1]
    
    # 基本动作语句
    def p_reply_statement(self, p):
        'reply_statement : REPLY expression'
        p[0] = self.create_node('Reply', value=p[2], lineno=p.lineno(1))
        
    def p_log_statement(self, p):
        'log_statement : LOG expression'
        p[0] = self.create_node('Log', value=p[2], lineno=p.lineno(1))

    def p_wait_statement(self, p):
        'wait_statement : WAIT string_list'
        p[0] = self.create_node('Wait', value=p[2], lineno=p.lineno(1))

    def p_string_list(self, p):
        '''string_list : string_list STRING
                    | STRING'''
        if len(p) == 3:
            p[0] = p[1] + [p[2]]
        else:
            p[0] = [p[1]]

    # 表达式
    def p_expression(self, p):
        '''expression : arithmetic_expression
                      | simple_expression'''
        p[0] = p[1]
    
    def p_arithmetic_expression(self, p):
        '''arithmetic_expression : expression PLUS expression'''
        p[0] = self.create_node('Arithmetic', [p[1], p[3]], p[2], p.lineno(2))
    
    def p_simple_expression(self, p):
        '''simple_expression : STRING
                            | VARIABLE
                            | ID'''  # 添加ID支持
        if p[1].startswith('$'):
            p[0] = self.create_node('Variable', value=p[1], lineno=p.lineno(1))
        elif p.slice[1].type == 'STRING':  # 明确检查token类型
            p[0] = self.create_node('String', value=p[1], lineno=p.lineno(1))
        else:  # ID token
            p[0] = self.create_node('Identifier', value=p[1], lineno=p.lineno(1))
    
    def p_error(self, p):
        if p:
            print(f"语法错误 at line {p.lineno}: token '{p.value}' (类型: {p.type})")
        else:
            print("语法错误: 意外的文件结束")
    
    def parse(self, data):
        """解析DSL脚本并返回字典格式的语法树"""
        try:
            result = self.parser.parse(input=data, lexer=self.lexer.lexer, debug=False)
            return result
        except Exception as e:
            print(f"解析错误: {e}")
            import traceback
            traceback.print_exc()
            return None