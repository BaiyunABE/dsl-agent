import ply.lex as lex
import ply.yacc as yacc

class Lexer:
    def __init__(self):
        self.lexer = None
        self.build()
    
    # Token 列表 - 添加MATCHES支持
    tokens = (
        # 区块关键字
        'CONFIG', 'VAR', 'FUNCTION', 'INTENT',
        
        # 动作关键字
        'REPLY', 'SET', 'IF', 'ELSE', 'END', 'CALL', 'LOG',
        
        # 运算符和分隔符
        'ASSIGN', 'EQUALS', 'PLUS', 'MINUS', 'TIMES', 'DIVIDE',
        'LPAREN', 'RPAREN', 'MATCHES',  # 添加MATCHES支持
        
        # 字面量
        'IDENTIFIER', 'STRING', 'NUMBER', 'VARIABLE',
    )
    
    # 关键字映射 - 添加matches支持
    reserved = {
        'config': 'CONFIG',
        'var': 'VAR', 
        'function': 'FUNCTION',
        'intent': 'INTENT',
        'reply': 'REPLY',
        'set': 'SET',
        'if': 'IF',
        'else': 'ELSE',
        'end': 'END',
        'call': 'CALL',
        'log': 'LOG',
        'matches': 'MATCHES',  # 添加matches支持
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
    t_MATCHES = r'matches'  # 添加matches token
    t_ignore = ' \t'
    
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

class DSLParser:
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
                  | function_section
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
    
    # Function 区块
    def p_function_section(self, p):
        'function_section : FUNCTION function_mappings'
        p[0] = self.create_node('FunctionSection', p[2], lineno=p.lineno(1))
    
    def p_function_mappings(self, p):
        '''function_mappings : function_mapping function_mappings
                            | function_mapping'''
        if len(p) == 3:
            p[0] = [p[1]] + p[2]
        else:
            p[0] = [p[1]]
    
    def p_function_mapping(self, p):
        'function_mapping : IDENTIFIER ASSIGN STRING'
        p[0] = self.create_node('FunctionMapping', [self.create_node('String', value=p[3])], p[1], p.lineno(1))
    
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
                      | IDENTIFIER ASSIGN IDENTIFIER LPAREN VARIABLE RPAREN'''
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
                     | matches_expression
                     | arithmetic_expression
                     | simple_expression'''
        p[0] = p[1]
    
    def p_comparison_expression(self, p):
        'comparison_expression : simple_expression EQUALS simple_expression'
        p[0] = self.create_node('Comparison', [p[1], p[3]], '==', p.lineno(2))
    
    def p_matches_expression(self, p):
        'matches_expression : simple_expression MATCHES STRING'
        p[0] = self.create_node('Matches', [p[1], p[3]], 'matches', p.lineno(2))
    
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
    
    # 使用修复后的脚本，将"else if"改为嵌套的"if"
    full_dsl = """
config
    default_intent = "greeting"
    timeout = 30
    max_retries = 3

var
    login_count = 0
    last_order = ""
    global_status = ""

function
    calc_delivery = "order_utils.calculate_delivery"
    validate_order = "order_utils.validate_order_id"

intent "greeting"
    reply "您好！欢迎光临！"
    reply "请问有什么可以帮您？"
    set login_count = $login_count + 1
    set global_status = ""
    log "用户问候，登录次数：$login_count，状态：$global_status"

intent "check_order"
    reply "正在查询订单信息..."
    set global_status = "check_order"
    reply "请问您要查询哪个订单号？"
    log "订单查询请求，状态：$global_status"

intent "provide_order_number"
    if $user_input matches "ORDER\\\\d+"
        set last_order = $user_input
        call is_valid = validate_order($user_input)

        if $is_valid
            reply "订单 $user_input 验证成功！"
            reply "订单状态：已发货"
            call delivery_date = calc_delivery($user_input)
            reply "预计送达时间：$delivery_date"
            
            if $global_status == "check_order"
                reply "订单查询完成，请问还需要其他帮助吗？"
            else
                if $global_status == "return_request"
                    reply "订单信息已确认，是否为此订单申请退货？"
                end
            end
        else
            reply "订单号 $user_input 无效或不存在"
        end
    else
        reply "订单号格式不正确，请提供类似 ORDER123 的格式"
    end
    log "订单号处理：$user_input，当前状态：$global_status"

intent "return_request"
    reply "了解您要退货的需求"
    set global_status = "return_request"
    reply "请提供需要退货的订单号"
    log "退货申请开始，状态：$global_status"

intent "confirm_return"
    reply "已为您提交订单 $last_order 的退货申请"
    reply "客服将在24小时内联系您处理后续事宜"
    reply "退货编号：RET123456"
    set global_status = ""
    log "退货确认完成，状态重置：$global_status"

intent "complaint"
    reply "抱歉给您带来不便"
    reply "请简要描述您遇到的问题："
    set global_status = "complaint"
    log "用户投诉受理，状态：$global_status"

intent "describe_issue"
    reply "感谢您的反馈，我们已经记录：$user_input"
    reply "客服专员将尽快联系您处理"
    reply "紧急问题可拨打热线：400-123-4567"
    set global_status = ""
    log "问题描述记录，状态：$global_status"

intent "ask_human_agent"
    reply "正在为您转接人工客服..."
    log "请求人工客服，状态：$global_status"

intent "unknown"
    if $global_status == "check_order"
        reply "抱歉，我没有理解您关于订单查询的请求"
        reply "请提供订单号（格式：ORDER123）或说明您的需求"
    else
        if $global_status == "return_request"
            reply "抱歉，我没有理解您关于退货的请求"
            reply "请提供订单号或确认是否申请退货"
        else
            reply "抱歉，我没有完全理解您的意思"
            reply "您可以尝试以下方式："
            reply "1. 查询订单状态"
            reply "2. 申请退货"
            reply "3. 联系人工客服"
            reply "请问您需要哪项服务？"
        end
    end
    log "未知意图处理：$user_input，当前状态：$global_status"

intent "thankyou"
    reply "不客气！"
    reply "祝您生活愉快！"
    set global_status = ""
    log "用户致谢，状态重置：$global_status"

intent "reset"
    reply "系统已重置"
    set login_count = 0
    set last_order = ""
    set global_status = ""
    log "系统重置操作，状态：$global_status"

intent "help"
    if $global_status == "check_order"
        reply "=== 订单查询帮助 ==="
        reply "请提供订单号（格式：ORDER123）"
        reply "或输入'返回'回到主菜单"
    else
        if $global_status == "return_request"
            reply "=== 退货申请帮助 ==="
            reply "请提供订单号或确认退货申请"
            reply "或输入'返回'取消退货流程"
        else
            reply "=== 可用功能 ==="
            reply "订单管理 - 查询订单、退货申请"
            reply "人工客服 - 转接人工服务"
            reply "系统重置 - 清除当前会话数据"
            reply "帮助信息 - 显示本提示"
        end
    end
    log "用户请求帮助，当前状态：$global_status"
"""
    
    parser = DSLParser(debug=False)
    ast_dict = parser.parse(full_dsl)
    
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
        matches = find_nodes_by_type(ast_dict, 'Matches')
        
        print(f"\n关键结构统计:")
        print(f"意图定义: {len(intents)} 个")
        print(f"函数调用: {len(calls)} 个")
        print(f"条件语句: {len(ifs)} 个")
        print(f"赋值操作: {len(sets)} 个")
        print(f"回复语句: {len(replies)} 个")
        print(f"日志语句: {len(logs)} 个")
        print(f"匹配操作: {len(matches)} 个")
        
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
"""
    
    parser = DSLParser(debug=False)
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