"""
增强版DSL脚本引擎
基于语法分析器的解释执行引擎
"""

import datetime
import os
import re
from typing import Dict, Any, List, Optional

# 导入parser模块
from parser import Parser

class DSLEngine:
    def __init__(self, script_file: str, debug: bool = False):
        """
        初始化DSL引擎
        
        Args:
            script_file: DSL脚本文件路径
            debug: 是否启用调试模式
        """
        # 解析脚本文件路径
        if not os.path.isabs(script_file):
            base_dir = os.path.dirname(__file__)
            self.script_file = os.path.join(base_dir, script_file)
        else:
            self.script_file = script_file
        
        self.debug = debug
        self.ast = None  # 抽象语法树
        self.variables = {}  # 变量存储
        self.functions = {}  # 函数映射
        self.registered_functions = {}  # 注册的Python函数
        self.current_intent = None  # 当前意图
        self.waiting_for = None  # 等待输入类型
        
        # 初始化内置函数
        self._init_builtin_functions()
        # 加载和解析脚本
        self._load_script()

    def _debug(self, msg: str):
        """调试信息输出"""
        if self.debug:
            print(f"[DEBUG] {msg}")

    def _init_builtin_functions(self):
        """初始化内置函数"""
        import re as _re
        import csv
        import os
        
        def calc_delivery(order_id=None):
            """根据订单号计算配送时间"""
            if not order_id or not isinstance(order_id, str):
                return "未知"
            
            # 从根目录的order.csv文件读取订单信息
            base_dir = os.path.dirname(os.path.dirname(__file__))  # 获取根目录
            csv_file = os.path.join(base_dir, "data", "order.csv")  # 数据目录
            
            try:
                with open(csv_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        # 检查订单号是否匹配
                        csv_order_num = row.get('订单号', '').strip()
                        input_order_num = order_id.replace('ORDER', '') if order_id.startswith('ORDER') else order_id
                        
                        if csv_order_num == input_order_num:
                            delivery_time = row.get('发货时间', '未知').strip()
                            return delivery_time if delivery_time else "未知"
                
                return "订单未找到"
            except FileNotFoundError:
                return "订单文件不存在"
            except Exception as e:
                self._debug(f"读取订单文件错误: {e}")
                return "系统错误"
        
        def validate_order(order_id=None):
            """验证订单号是否存在"""
            if not order_id or not isinstance(order_id, str):
                return False
            
            # 检查格式
            if not _re.fullmatch(r"ORDER\d+", order_id):
                return False
            
            # 从根目录的order.csv文件验证订单是否存在
            base_dir = os.path.dirname(os.path.dirname(__file__))  # 获取根目录
            csv_file = os.path.join(base_dir, "data", "order.csv")  # 数据目录
            
            try:
                with open(csv_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        csv_order_num = row.get('订单号', '').strip()
                        input_order_num = order_id.replace('ORDER', '')
                        
                        if csv_order_num == input_order_num:
                            return True
                return False
            except FileNotFoundError:
                self._debug("订单文件不存在")
                return False
            except Exception as e:
                self._debug(f"验证订单错误: {e}")
                return False
        
        # 注册内置函数
        self.register_function('calc_delivery', calc_delivery)
        self.register_function('validate_order', validate_order)


    def register_function(self, name: str, func):
        """注册Python函数供DSL调用"""
        self.registered_functions[name] = func
        self._debug(f"注册函数: {name}")

    def _load_script(self):
        """加载和解析DSL脚本"""
        try:
            with open(self.script_file, 'r', encoding='utf-8') as f:
                script_content = f.read()
            
            # 使用parser解析脚本
            parser = Parser(debug=self.debug)
            self.ast = parser.parse(script_content)
            
            if not self.ast:
                raise Exception("脚本解析失败")
            
            self._debug("脚本解析成功")
            self._extract_config_and_vars()
            
        except FileNotFoundError:
            raise Exception(f"脚本文件不存在: {self.script_file}")
        except Exception as e:
            raise Exception(f"脚本加载失败: {e}")

    def _extract_config_and_vars(self):
        """从AST中提取配置和变量初始值"""
        if not self.ast or 'children' not in self.ast:
            return
        
        for section in self.ast['children']:
            if section['type'] == 'ConfigSection':
                self._process_config_section(section)
            elif section['type'] == 'VarSection':
                self._process_var_section(section)
            elif section['type'] == 'FunctionSection':
                self._process_function_section(section)

    def _process_config_section(self, config_section):
        """处理配置区块"""
        for item in config_section.get('children', []):
            if item['type'] == 'ConfigItem':
                var_name = item.get('value', '')
                # 配置项的值在第一个子节点中
                if item.get('children'):
                    value_node = item['children'][0]
                    value = self._evaluate_expression(value_node)
                    self.variables[var_name] = value
                    self._debug(f"配置: {var_name} = {value}")

    def _process_var_section(self, var_section):
        """处理变量区块"""
        for item in var_section.get('children', []):
            if item['type'] == 'VarDeclaration':
                var_name = item.get('value', '')
                # 变量初始值在第一个子节点中
                if item.get('children'):
                    value_node = item['children'][0]
                    value = self._evaluate_expression(value_node)
                    self.variables[var_name] = value
                    self._debug(f"变量: {var_name} = {value}")

    def _process_function_section(self, function_section):
        """处理函数映射区块"""
        for item in function_section.get('children', []):
            if item['type'] == 'FunctionMapping':
                func_name = item.get('value', '')
                # 函数映射值在第一个子节点中
                if item.get('children'):
                    value_node = item['children'][0]
                    if value_node['type'] == 'String':
                        self.functions[func_name] = value_node.get('value', '')
                        self._debug(f"函数映射: {func_name} -> {self.functions[func_name]}")

    def _evaluate_expression(self, node: Dict) -> Any:
        """评估表达式节点"""
        if not isinstance(node, dict):
            return node

        node_type = node.get('type', '')
        
        if node_type == 'String':
            return node.get('value', '')
        elif node_type == 'Number':
            return node.get('value', 0)
        elif node_type == 'Variable':
            var_name = node.get('value', '')
            # 去掉$前缀
            if var_name.startswith('$'):
                var_name = var_name[1:]
            return self.variables.get(var_name, '')
        elif node_type == 'Identifier':
            return node.get('value', '')
        elif node_type == 'Arithmetic':
            return self._evaluate_arithmetic(node)
        elif node_type == 'Comparison':
            return self._evaluate_comparison(node)
        elif node_type == 'Matches':
            return self._evaluate_matches(node)
        else:
            self._debug(f"未知表达式类型: {node_type}")
            return None

    def _evaluate_arithmetic(self, node: Dict) -> Any:
        """评估算术表达式"""
        if not node.get('children') or len(node['children']) != 2:
            return 0
        
        left = self._evaluate_expression(node['children'][0])
        right = self._evaluate_expression(node['children'][1])
        operator = node.get('value', '')
        
        try:
            if operator == '+':
                # 支持字符串连接和数字相加
                if isinstance(left, str) or isinstance(right, str):
                    return str(left) + str(right)
                return left + right
            elif operator == '-':
                return left - right
            elif operator == '*':
                return left * right
            elif operator == '/':
                return left / right if right != 0 else 0
            else:
                return 0
        except Exception as e:
            self._debug(f"算术运算错误: {e}")
            return 0

    def _evaluate_comparison(self, node: Dict) -> bool:
        """评估比较表达式"""
        if not node.get('children') or len(node['children']) != 2:
            return False
        
        left = self._evaluate_expression(node['children'][0])
        right = self._evaluate_expression(node['children'][1])
        operator = node.get('value', '')
        
        try:
            if operator == '==':
                return left == right
            else:
                return False
        except Exception as e:
            self._debug(f"比较运算错误: {e}")
            return False

    def _evaluate_matches(self, node: Dict) -> bool:
        """评估正则匹配表达式"""
        if not node.get('children') or len(node['children']) != 2:
            return False
        
        left = self._evaluate_expression(node['children'][0])
        pattern = self._evaluate_expression(node['children'][1])
        
        try:
            if isinstance(left, str) and isinstance(pattern, str):
                pattern = pattern.encode().decode('unicode_escape')
                self._debug(f"正则匹配: '{left}' 匹配模式 '{pattern}'")
                return bool(re.fullmatch(pattern, left))
            return False
        except Exception as e:
            self._debug(f"正则匹配错误: {e}")
            return False

    def _execute_statement(self, statement: Dict, user_input: str = '') -> List[str]:
        """执行单个语句"""
        responses = []
        node_type = statement.get('type', '')
        
        if node_type == 'Reply':
            # 处理回复语句
            reply_text = statement.get('value', '')
            # 替换变量
            reply_text = self._replace_variables(reply_text, user_input)
            responses.append(reply_text)
            
        elif node_type == 'Set':
            # 处理赋值语句
            var_name = statement.get('value', '')
            if statement.get('children'):
                value_node = statement['children'][0]
                value = self._evaluate_expression(value_node)
                self.variables[var_name] = value
                self._debug(f"设置变量: {var_name} = {value}")
                
        elif node_type == 'Log':
            # 处理日志语句
            log_text = statement.get('value', '')
            log_text = self._replace_variables(log_text, user_input)
            
            # 写入日志文件
            log_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'log', 'todo.log')
            os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
            
            # 带时间戳的日志
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] {log_text}\n"
            
            try:
                with open(log_file_path, 'a', encoding='utf-8') as log_file:
                    log_file.write(log_entry)
            except Exception as e:
                print(f"❌ 写入日志文件失败: {e}")
            
        elif node_type == 'Call':
            # 处理函数调用
            if statement.get('children'):
                assignment_node = statement['children'][0]
                self._execute_function_call(assignment_node, user_input)
                
        elif node_type == 'IfStatement':
            # 处理条件语句
            responses.extend(self._execute_if_statement(statement, user_input))
            
        return responses

    def _execute_if_statement(self, if_node: Dict, user_input: str) -> List[str]:
        """执行条件语句"""
        responses = []
        
        if not if_node.get('children'):
            return responses
        
        # 第一个子节点是条件表达式
        condition_node = if_node['children'][0]
        condition_result = self._evaluate_expression(condition_node)
        
        self._debug(f"条件评估: {condition_result}")
        
        if condition_result:
            # 执行then分支
            for i in range(1, len(if_node['children'])):
                child = if_node['children'][i]
                if child['type'] in ['ThenBranch', 'ElseBranch']:
                    # 执行分支中的语句
                    for stmt in child.get('children', []):
                        responses.extend(self._execute_statement(stmt, user_input))
                    break
                else:
                    # 直接执行语句
                    responses.extend(self._execute_statement(child, user_input))
        else:
            # 查找else分支
            found_then = False
            for i in range(1, len(if_node['children'])):
                child = if_node['children'][i]
                if child['type'] == 'ThenBranch':
                    found_then = True
                elif child['type'] == 'ElseBranch' and found_then:
                    # 执行else分支
                    for stmt in child.get('children', []):
                        responses.extend(self._execute_statement(stmt, user_input))
                    break
        
        return responses

    def _execute_function_call(self, assignment_node: Dict, user_input: str):
        """执行函数调用"""
        if assignment_node['type'] != 'Assignment':
            return
        
        # 获取变量名和函数调用
        var_name = assignment_node.get('value', '')
        if not assignment_node.get('children'):
            return
        
        func_call_node = assignment_node['children'][0]
        if func_call_node['type'] != 'FunctionCall':
            return
        
        func_name = func_call_node.get('value', '')
        
        # 准备参数 - 修复参数解析
        args = []
        if func_call_node.get('children'):
            for arg_node in func_call_node['children']:
                # 先评估参数表达式，获取实际值
                arg_value = self._evaluate_expression(arg_node)
                # 确保 user_input 被正确替换
                if arg_value == '$user_input':
                    arg_value = user_input
                args.append(arg_value)
        
        self._debug(f"调用函数 {func_name}，参数: {args}")
        
        # 调用函数
        result = None
        if func_name in self.registered_functions:
            try:
                result = self.registered_functions[func_name](*args)
                self._debug(f"函数调用结果: {func_name}({args}) = {result}")
            except Exception as e:
                self._debug(f"函数调用错误: {e}")
        else:
            self._debug(f"未注册的函数: {func_name}")
        
        # 存储结果
        if result is not None:
            self.variables[var_name] = result

    def _replace_variables(self, text: str, user_input: str) -> str:
        """替换文本中的变量引用"""
        def replace_match(match):
            var_name = match.group(1)
            if var_name == 'user_input':
                return user_input
            return str(self.variables.get(var_name, ''))
        
        # 替换 $变量名 格式
        result = re.sub(r'\$(\w+)', replace_match, text)
        return result

    def get_intents(self) -> List[str]:
        """获取所有可用的意图名称"""
        intents = []
        if not self.ast or 'children' not in self.ast:
            return intents
        
        for section in self.ast['children']:
            if section['type'] == 'Intent':
                intent_name = section.get('value', '')
                if intent_name:
                    intents.append(intent_name)
        
        return intents

    def process(self, intent_name: str, user_input: str = '') -> str:
        """处理意图并生成回复"""
        self._debug(f"处理意图: {intent_name}, 输入: {user_input}")
        
        # 设置用户输入变量 - 确保在表达式求值前设置
        self.variables['user_input'] = user_input
        
        # 查找匹配的意图
        target_intent = None
        if self.ast and 'children' in self.ast:
            for section in self.ast['children']:
                if section['type'] == 'Intent' and section.get('value') == intent_name:
                    target_intent = section
                    break
        
        if not target_intent:
            return f"未知意图: {intent_name}"
        
        # 执行意图中的语句
        responses = []
        for statement in target_intent.get('children', []):
            responses.extend(self._execute_statement(statement, user_input))
        
        # 更新当前意图
        self.current_intent = intent_name
        
        return '\n'.join(responses) if responses else ""

    def get_waiting_status(self) -> Optional[str]:
        """获取当前等待状态"""
        return self.waiting_for

    def reset(self):
        """重置引擎状态"""
        self.variables.clear()
        self.current_intent = None
        self.waiting_for = None
        # 重新加载配置和变量初始值
        self._extract_config_and_vars()

    def get_variables(self) -> Dict[str, Any]:
        """获取当前变量状态"""
        return self.variables.copy()

# 测试函数
def test_engine():
    """测试DSL引擎"""
    print("=== 测试DSL引擎 ===")

    script_path = "script.dsl"
    
    try:
        # 创建引擎
        engine = DSLEngine(script_path, debug=True)

        # 测试可用意图
        intents = engine.get_intents()
        print(f"可用意图: {intents}")

        print("\n" + "="*50)
        print("测试1: 正常流程测试")
        print("="*50)

        # 测试正常流程
        response1 = engine.process("greeting")
        print("响应1 - greeting:")
        print(response1)
        print(f"当前变量: {engine.get_variables()}")

        response2 = engine.process("provide_order_number", "ORDER123")
        print("响应2 - provide_order_number ORDER123:")
        print(response2)
        print(f"当前变量: {engine.get_variables()}")

        print("\n" + "="*50)
        print("测试2: 边界值测试")
        print("="*50)

        # 测试边界值
        response3 = engine.process("provide_order_number", "")  # 空订单号
        print("响应3 - 空订单号:")
        print(response3)

        response4 = engine.process("provide_order_number", "ORDER")  # 只有ORDER前缀
        print("响应4 - 只有ORDER前缀:")
        print(response4)

        response5 = engine.process("provide_order_number", "123")  # 没有ORDER前缀
        print("响应5 - 没有ORDER前缀:")
        print(response5)

        print("\n" + "="*50)
        print("测试3: 错误处理测试")
        print("="*50)

        # 测试错误处理
        response6 = engine.process("unknown_intent")  # 不存在的意图
        print("响应6 - 未知意图:")
        print(response6)

        # response7 = engine.process("provide_order_number", "ORDER123", "extra_param")  # 多余参数
        # print("响应7 - 多余参数:")
        # print(response7)

        response8 = engine.process("greeting", "unexpected_param")  # 不应有参数的意图
        print("响应8 - greeting带参数:")
        print(response8)

        print("\n" + "="*50)
        print("测试4: 重复操作测试")
        print("="*50)

        # 测试重复操作
        response9 = engine.process("provide_order_number", "ORDER456")  # 新订单号
        print("响应9 - 新订单号ORDER456:")
        print(response9)
        print(f"当前变量: {engine.get_variables()}")

        response10 = engine.process("provide_order_number", "ORDER456")  # 重复相同订单号
        print("响应10 - 重复ORDER456:")
        print(response10)

        print("\n" + "="*50)
        print("测试5: 特殊字符测试")
        print("="*50)

        # 测试特殊字符
        special_cases = [
            "ORDER 123",      # 带空格
            "ORDER-123",      # 带连字符
            "ORDER_123",      # 带下划线
            "ORDER123 ",      # 末尾空格
            " ORDER123",      # 开头空格
            "ORDER123ABC",    # 字母数字混合
            "123ORDER",       # 后缀ORDER
        ]

        for i, case in enumerate(special_cases, 1):
            response = engine.process("provide_order_number", case)
            print(f"响应{10+i} - 特殊案例 '{case}':")
            print(response)

        print("\n" + "="*50)
        print("测试6: 变量状态测试")
        print("="*50)

        # 检查变量状态
        variables = engine.get_variables()
        print("最终变量状态:")
        for key, value in variables.items():
            print(f"  {key}: {value}")

        print("\n" + "="*50)
        print("测试7: 重置功能测试")
        print("="*50)

        # 测试重置
        engine.reset()
        reset_variables = engine.get_variables()
        print(f"重置后变量: {reset_variables}")

        # 重置后重新测试
        response_reset = engine.process("greeting")
        print("重置后greeting响应:")
        print(response_reset)

        print("\n" + "="*50)
        print("测试8: 性能测试")
        print("="*50)

        # 简单性能测试
        import time

        start_time = time.time()
        for i in range(100):  # 快速调用100次
            engine.process("greeting")
        end_time = time.time()

        print(f"100次greeting调用耗时: {end_time - start_time:.4f}秒")

        # 测试订单号查找性能
        start_time = time.time()
        for i in range(50):
            engine.process("provide_order_number", f"ORDER{i:03d}")
        end_time = time.time()
        print(f"50次订单查询耗时: {end_time - start_time:.4f}秒")

        print("\n" + "="*50)
        print("测试完成")
        print("="*50)
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # 清理测试文件
        if os.path.exists(script_path):
            os.remove(script_path)
            print(f"✅ 测试脚本已清理: {script_path}")

if __name__ == "__main__":
    test_engine()