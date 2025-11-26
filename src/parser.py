import os
import ply.lex as lex
import ply.yacc as yacc

class Lexer:
    def __init__(self):
        self.lexer = None
        self.build()
    
    tokens = (
        # 区块关键字
        'CONFIG', 'VAR', 'INTENT',
        
        # 动作关键字
        'REPLY', 'SET', 'IF', 'ELSE', 'END', 'CALL', 'LOG',
        
        # 运算符和分隔符
        'ASSIGN', 'EQUALS', 'PLUS', 'MINUS', 'TIMES', 'DIVIDE',
        'LPAREN', 'RPAREN',
        
        # 字面量
        'IDENTIFIER', 'STRING', 'NUMBER', 'VARIABLE',
    )
    
    reserved = {
        'config': 'CONFIG',
        'var': 'VAR', 
        'intent': 'INTENT',
        'reply': 'REPLY',
        'set': 'SET',
        'if': 'IF',
        'else': 'ELSE',
        'end': 'END',
        'call': 'CALL',
        'log': 'LOG',
    }
    
    # 简单token规则
    t_ASSIGN = r'='
    t_EQUALS = r'=='
    t_PLUS = r'\+'
    t_MINUS = r'-'
    t_TIMES = r'\*'
    t_DIVIDE = r'/'
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_ignore = ' \t'
    
    # 注释处理规则
    def t_COMMENT(self, t):
        r'\#.*'
        print(f"Skipping comment: {t.value}")
        # 注释不返回token，直接跳过
        pass

    # 复杂token规则
    def t_IDENTIFIER(self, t):
        r'[a-zA-Z_][a-zA-Z0-9_]*'
        t.type = self.reserved.get(t.value.lower(), 'IDENTIFIER')
        return t
    
    def t_VARIABLE(self, t):
        r'\$[a-zA-Z_][a-zA-Z0-9_]*'
        return t
    
    def t_STRING(self, t):
        r'\"([^\"\\]|\\.)*\"'
        t.value = t.value[1:-1]
        return t
    
    def t_NUMBER(self, t):
        r'\d+(\.\d+)?'
        t.value = float(t.value) if '.' in t.value else int(t.value)
        return t
    
    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)
    
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
        '''section : config_section
                  | var_section
                  | intent_section'''
        p[0] = p[1]
    
    # Config 区块
    def p_config_section(self, p):
        'config_section : CONFIG config_items'
        p[0] = self.create_node('ConfigSection', p[2], lineno=p.lineno(1))
    
    def p_config_items(self, p):
        '''config_items : config_item config_items
                        | config_item'''
        if len(p) == 3:
            p[0] = [p[1]] + p[2]
        else:
            p[0] = [p[1]]
    
    def p_config_item(self, p):
        'config_item : IDENTIFIER ASSIGN expression'
        p[0] = self.create_node('ConfigItem', [p[3]], p[1], p.lineno(1))
    
    # Var 区块
    def p_var_section(self, p):
        'var_section : VAR var_declarations'
        p[0] = self.create_node('VarSection', p[2], lineno=p.lineno(1))
    
    def p_var_declarations(self, p):
        '''var_declarations : var_declaration var_declarations
                           | var_declaration'''
        if len(p) == 3:
            p[0] = [p[1]] + p[2]
        else:
            p[0] = [p[1]]
    
    def p_var_declaration(self, p):
        'var_declaration : IDENTIFIER ASSIGN expression'
        p[0] = self.create_node('VarDeclaration', [p[3]], p[1], p.lineno(1))
    
    # Intent 区块
    def p_intent_section(self, p):
        'intent_section : INTENT STRING statements'
        p[0] = self.create_node('Intent', p[3], p[2], p.lineno(1))
    
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
                    | set_statement
                    | if_statement
                    | call_statement
                    | log_statement'''
        p[0] = p[1]
    
    # 基本动作语句
    def p_reply_statement(self, p):
        'reply_statement : REPLY STRING'
        p[0] = self.create_node('Reply', value=p[2], lineno=p.lineno(1))
    
    def p_set_statement(self, p):
        'set_statement : SET IDENTIFIER ASSIGN expression'
        p[0] = self.create_node('Set', [p[4]], p[2], p.lineno(1))
    
    def p_log_statement(self, p):
        'log_statement : LOG STRING'
        p[0] = self.create_node('Log', value=p[2], lineno=p.lineno(1))
    
    def p_call_statement(self, p):
        'call_statement : CALL assignment'
        p[0] = self.create_node('Call', [p[2]], lineno=p.lineno(1))
    
    def p_assignment(self, p):
        '''assignment : IDENTIFIER ASSIGN IDENTIFIER LPAREN RPAREN
                      | IDENTIFIER ASSIGN IDENTIFIER LPAREN expression RPAREN'''
        # call result = function_name() 或 call result = function_name($user_input)
        if len(p) == 6:  # 无参数
            func_call = self.create_node('FunctionCall', value=p[3], lineno=p.lineno(1))
            p[0] = self.create_node('Assignment', [func_call], p[1], p.lineno(1))
        else:  # 有参数
            func_call = self.create_node('FunctionCall', [p[5]], p[3], p.lineno(1))
            p[0] = self.create_node('Assignment', [func_call], p[1], p.lineno(1))
    
    # 条件语句 - 修复嵌套if支持
    def p_if_statement(self, p):
        '''if_statement : IF expression statements END
                       | IF expression statements ELSE statements END
                       | IF expression statements ELSE if_statement'''
        if len(p) == 5:  # if ... end
            p[0] = self.create_node('IfStatement', [p[2]] + p[3], lineno=p.lineno(1))
        elif len(p) == 6:  # if ... else if ... (嵌套)
            then_branch = self.create_node('ThenBranch', p[3], lineno=p.lineno(1))
            else_branch = self.create_node('ElseBranch', [p[4]], lineno=p.lineno(1))
            p[0] = self.create_node('IfStatement', [p[2], then_branch, else_branch], lineno=p.lineno(1))
        else:  # if ... else ... end
            then_branch = self.create_node('ThenBranch', p[3], lineno=p.lineno(1))
            else_branch = self.create_node('ElseBranch', p[5], lineno=p.lineno(1))
            p[0] = self.create_node('IfStatement', [p[2], then_branch, else_branch], lineno=p.lineno(1))
    
    # 表达式
    def p_expression(self, p):
        '''expression : comparison_expression
                     | arithmetic_expression
                     | simple_expression'''
        p[0] = p[1]
    
    def p_comparison_expression(self, p):
        'comparison_expression : simple_expression EQUALS simple_expression'
        p[0] = self.create_node('Comparison', [p[1], p[3]], '==', p.lineno(2))
    
    def p_arithmetic_expression(self, p):
        '''arithmetic_expression : expression PLUS expression
                                | expression MINUS expression
                                | expression TIMES expression
                                | expression DIVIDE expression'''
        p[0] = self.create_node('Arithmetic', [p[1], p[3]], p[2], p.lineno(2))
    
    def p_simple_expression(self, p):
        '''simple_expression : STRING
                            | NUMBER
                            | VARIABLE
                            | IDENTIFIER'''
        if isinstance(p[1], str):
            if p[1].startswith('$'):
                p[0] = self.create_node('Variable', value=p[1], lineno=p.lineno(1))
            else:
                p[0] = self.create_node('String', value=p[1], lineno=p.lineno(1))
        elif isinstance(p[1], (int, float)):
            p[0] = self.create_node('Number', value=p[1], lineno=p.lineno(1))
        else:
            p[0] = self.create_node('Identifier', value=p[1], lineno=p.lineno(1))
    
    def p_error(self, p):
        if p:
            print(f"语法错误 at line {p.lineno}: token '{p.value}'")
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

def print_tree(node, indent=0):
    """以树形结构打印字典格式的语法树"""
    if not isinstance(node, dict):
        print("  " * indent + str(node))
        return
    
    node_type = node.get('type', 'Unknown')
    value = node.get('value', '')
    lineno = node.get('lineno', '')
    
    # 构建节点显示字符串
    node_str = f"{node_type}"
    if value:
        node_str += f"({repr(value)})"
    if lineno:
        node_str += f" [line:{lineno}]"
    
    print("  " * indent + node_str)
    
    # 递归打印子节点
    if 'children' in node:
        for child in node['children']:
            print_tree(child, indent + 1)

def count_nodes(node):
    """统计语法树节点数量"""
    if not isinstance(node, dict):
        return 1
    
    count = 1
    if 'children' in node:
        for child in node['children']:
            count += count_nodes(child)
    return count

def test_full_script():
    """测试您的完整DSL脚本"""
    print("\n=== 测试完整DSL脚本 ===")
    
    base_dir = os.path.dirname(__file__)
    script_path = os.path.join(base_dir, "script.dsl")
    script_content = ""

    with open(script_path, 'r', encoding='utf-8') as f:
        script_content = f.read()

    parser = Parser(debug=False)
    ast_dict = parser.parse(script_content)
    
    if ast_dict:
        print("✅ 完整脚本解析成功！")
        print(f"语法树总节点数: {count_nodes(ast_dict)}")
        
        # 验证关键结构
        def find_nodes_by_type(node, target_type, results=None):
            if results is None:
                results = []
            
            if isinstance(node, dict):
                if node.get('type') == target_type:
                    results.append(node)
                
                if 'children' in node:
                    for child in node['children']:
                        find_nodes_by_type(child, target_type, results)
            
            return results
        
        # 检查关键节点
        intents = find_nodes_by_type(ast_dict, 'Intent')
        calls = find_nodes_by_type(ast_dict, 'Call')
        ifs = find_nodes_by_type(ast_dict, 'IfStatement')
        sets = find_nodes_by_type(ast_dict, 'Set')
        replies = find_nodes_by_type(ast_dict, 'Reply')
        logs = find_nodes_by_type(ast_dict, 'Log')
        
        print(f"\n关键结构统计:")
        print(f"意图定义: {len(intents)} 个")
        print(f"函数调用: {len(calls)} 个")
        print(f"条件语句: {len(ifs)} 个")
        print(f"赋值操作: {len(sets)} 个")
        print(f"回复语句: {len(replies)} 个")
        print(f"日志语句: {len(logs)} 个")
        
        # 显示前几个意图的结构
        print(f"\n前3个意图的结构:")
        intent_count = 0
        for node in ast_dict.get('children', []):
            if node.get('type') == 'Intent' and intent_count < 3:
                print(f"\n意图: {node.get('value')}")
                intent_children = node.get('children', [])
                print(f"  语句数: {len(intent_children)}")
                intent_count += 1
        
        # 保存到文件
        import json
        try:
            with open('ast_output.json', 'w', encoding='utf-8') as f:
                json.dump(ast_dict, f, ensure_ascii=False, indent=2)
            print(f"\n✅ 语法树已保存到 ast_output.json")
        except Exception as e:
            print(f"❌ 保存文件失败: {e}")
            
    else:
        print("❌ 完整脚本解析失败")

def test_simple_parser():
    """测试简化版的语法分析器"""
    print("\n=== 测试简化版语法分析器 ===")
    
    simple_dsl = """
config
    default_intent = "greeting"
    timeout = 30

var
    login_count = 0

intent "greeting"
    reply "Hello World"
    set login_count = $login_count + 1
    call res = extract_order_number($user_input)
"""
    
    parser = Parser(debug=False)
    ast_dict = parser.parse(simple_dsl)
    
    if ast_dict:
        print("简化版解析成功！")
        print("树形结构:")
        print_tree(ast_dict)
        
        # 显示字典结构
        print("\n字典结构验证:")
        print(f"类型: {type(ast_dict)}")
        print(f"根节点键: {list(ast_dict.keys())}")
        print(f"根节点类型: {ast_dict.get('type')}")
        print(f"子节点数: {len(ast_dict.get('children', []))}")
    else:
        print("简化版解析失败")

if __name__ == "__main__":
    test_simple_parser()
    test_full_script()