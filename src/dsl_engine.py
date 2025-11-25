"""
增强版DSL脚本引擎
解析和执行增强版DSL脚本文件，支持变量、条件判断、函数调用等高级功能
"""

import os
import re
import random
import time
from typing import Dict, Any, List, Tuple
import ast

class DSLEngine:
    def __init__(self, script_file, debug: bool = False):
        # Resolve script path relative to this module so tests and CLI work
        if not os.path.isabs(script_file):
            base_dir = os.path.dirname(__file__)
            self.script_file = os.path.join(base_dir, script_file)
        else:
            self.script_file = script_file
        self.scenes = {}  # 存储解析后的场景和意图
        self.config = {}  # 配置参数
        self.variables = {}  # 变量存储
        self.functions = {}  # 函数映射
        self.registered_functions = {}  # name -> callable
        self.waiting_for = None  # 等待用户输入的类型
        self.debug = debug
        self._load_script()

    def _debug(self, msg: str):
        """条件性打印调试信息，在 `debug=True` 时输出。"""
        if getattr(self, 'debug', False):
            print(msg)

    def _load_script(self):
        """加载和解析增强版DSL脚本文件"""
        try:
            with open(self.script_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # 初始化默认配置和变量
            self._init_defaults()

            # 解析脚本内容
            lines = content.split('\n')
            i = 0
            current_section = None
            current_scene = None
            current_intent = None
            current_condition_stack = []  # 条件栈，用于处理嵌套条件

            while i < len(lines):
                line = lines[i].strip()

                # 跳过空行和注释
                if not line or line.startswith('#'):
                    i += 1
                    continue

                # 解析配置区块
                if line == 'config':
                    current_section = 'config'
                    i += 1
                    continue
                elif line == 'var':
                    current_section = 'var'
                    i += 1
                    continue
                elif line == 'function':
                    current_section = 'function'
                    i += 1
                    continue
                elif line.startswith('scene '):
                    current_section = 'scene'
                    scene_name = line.split('"')[1]
                    current_scene = scene_name
                    self.scenes[scene_name] = {}
                    i += 1
                    continue

                # 根据当前区块解析内容
                if current_section == 'config':
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        # 尝试转换数值类型
                        if value.isdigit():
                            self.config[key] = int(value)
                        elif value.replace('.', '').isdigit():
                            self.config[key] = float(value)
                        else:
                            self.config[key] = value

                elif current_section == 'var':
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        # 尝试转换数值类型
                        if value.isdigit():
                            self.variables[key] = int(value)
                        elif value.replace('.', '').isdigit():
                            self.variables[key] = float(value)
                        else:
                            self.variables[key] = value.strip('"')

                elif current_section == 'function':
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"')
                        self.functions[key] = value

                elif current_section == 'scene':
                    if line.startswith('intent '):
                        intent_name = line.split('"')[1]
                        current_intent = intent_name
                        self.scenes[current_scene][intent_name] = []
                        i += 1
                        continue

                    elif current_intent and line.startswith('reply '):
                        reply_text = line.split('"')[1]
                        action = ('reply', reply_text, current_condition_stack.copy())
                        self.scenes[current_scene][current_intent].append(action)

                    elif current_intent and line.startswith('log '):
                        log_text = line.split('"')[1]
                        action = ('log', log_text, current_condition_stack.copy())
                        self.scenes[current_scene][current_intent].append(action)

                    elif current_intent and line.startswith('set '):
                        set_expr = line[4:].strip()
                        action = ('set', set_expr, current_condition_stack.copy())
                        self.scenes[current_scene][current_intent].append(action)

                    elif current_intent and line.startswith('call '):
                        call_expr = line[5:].strip()
                        action = ('call', call_expr, current_condition_stack.copy())
                        self.scenes[current_scene][current_intent].append(action)

                    elif current_intent and line.startswith('wait_for_input '):
                        wait_type = line.split('"')[1]
                        action = ('wait_for_input', wait_type, current_condition_stack.copy())
                        self.scenes[current_scene][current_intent].append(action)

                    elif current_intent and line.startswith('wait_for_confirm '):
                        wait_type = line.split('"')[1]
                        action = ('wait_for_confirm', wait_type, current_condition_stack.copy())
                        self.scenes[current_scene][current_intent].append(action)

                    elif current_intent and line.startswith('extract '):
                        extract_expr = line[8:].strip()
                        action = ('extract', extract_expr, current_condition_stack.copy())
                        self.scenes[current_scene][current_intent].append(action)

                    elif current_intent and line.startswith('if '):
                        # 解析条件表达式
                        condition_expr = line[3 if line.startswith('if ') else 10:].strip()
                        current_condition_stack.append(('if', condition_expr))

                    elif current_intent and line.startswith('condition ') and 'matches' in line:
                        # 处理matches条件中的转义
                        condition_expr = line[10:].strip()
                        # 修复正则表达式中的转义
                        condition_expr = condition_expr.replace('\\\\d', '\\d')
                        current_condition_stack.append(('if', condition_expr))

                    elif current_intent and line == 'else':
                        # 将上一个if转换为else
                        if current_condition_stack and current_condition_stack[-1][0] == 'if':
                            last_if = current_condition_stack.pop()
                            current_condition_stack.append(('else', last_if[1]))

                    elif current_intent and line == 'end':
                        if current_condition_stack:
                            current_condition_stack.pop()

                i += 1

        except FileNotFoundError:
            # 如果文件不存在，使用内置的默认脚本
            print("📝 使用内置默认脚本")
            self._create_default_script()
        except Exception as e:
            print(f"❌ 脚本解析错误: {e}")
            self._create_default_script()

    def _init_defaults(self):
        """初始化默认配置和变量"""
        self.config = {
            'default_scene': 'main',
            'timeout': 30,
            'max_retries': 3
        }
        self.variables = {
            'user_name': '访客',
            'login_count': 0,
            'last_order': '',
            'current_time': ''
        }
        self.functions = {}
        self.registered_functions = {}
        self.waiting_for = None

        # 注册内置示例函数，便于在测试和主程序中直接使用 `call` 调用
        try:
            import time as _time
            import re as _re

            def _get_time():
                return _time.strftime("%Y-%m-%d %H:%M:%S")

            def _calc_delivery(order_id=None):
                # 简化示例实现：如果有订单号则返回示例时间，否则返回空字符串
                return "明天下午" if order_id else "未知"

            def _validate_order(order_id=None):
                if not order_id or not isinstance(order_id, str):
                    return False
                # 简单规则：以 ORDER 开头且后接数字
                return bool(_re.fullmatch(r"ORDER\d+", order_id))

            self.register_function('get_time', _get_time)
            self.register_function('calc_delivery', _calc_delivery)
            self.register_function('validate_order', _validate_order)
        except Exception:
            pass

    def register_function(self, name: str, func):
        """注册可供 `call` 使用的 Python 回调函数。"""
        self.registered_functions[name] = func

    def _create_default_script(self):
        """创建默认的DSL脚本（防止文件不存在）"""
        self._init_defaults()
        self.scenes = {
            'greeting': {
                'greeting': [
                    ('reply', '你好！我是智能客服机器人', []),
                    ('reply', '有什么可以帮您的吗？', []),
                    ('log', '用户打招呼', [])
                ]
            },
            'support': {
                'ask_time': [
                    ('reply', '当前时间是：2024年1月1日 10:00', []),
                    ('log', '用户询问时间', [])
                ],
                'check_order': [
                    ('reply', '正在查询您的订单...', []),
                    ('reply', '订单状态：已发货', []),
                    ('log', '用户查询订单', [])
                ]
            }
        }

    def _evaluate_condition(self, condition: str, user_input: str) -> bool:
        """评估条件表达式"""
        try:
            # 标准化条件输入，支持传入带前缀的字符串如 'condition ...' 或 'if ...'
            condition = condition.strip()
            if condition.startswith('condition '):
                condition = condition[len('condition '):].strip()
            if condition.startswith('if '):
                condition = condition[len('if '):].strip()

            # 首先替换用户输入引用
            condition = condition.replace('$user_input', f'"{user_input}"')

            # 然后替换其他变量
            condition = self._replace_variables(condition)

            self._debug(f"[DEBUG] 评估条件: {condition}, 用户输入: {user_input}")

            # 解析contains操作
            if ' contains ' in condition:
                parts = condition.split(' contains ', 1)
                left = parts[0].strip()
                right = parts[1].strip().strip('"\'')

                # 处理左侧值
                if left.startswith('"') and left.endswith('"'):
                    left_value = left[1:-1]  # 去除引号
                else:
                    left_value = left
                self._debug(f"[DEBUG] contains检查: '{left_value}' 包含 '{right}'")
                return right in left_value

            # 解析matches操作
            elif ' matches ' in condition:
                parts = condition.split(' matches ', 1)
                left = parts[0].strip()
                right = parts[1].strip().strip('"\'')

                # 处理左侧值
                if left.startswith('"') and left.endswith('"'):
                    left_value = left[1:-1]  # 去除引号
                else:
                    left_value = left

                # 规范化 pattern（用户脚本里可能用双反斜杠写法）
                try:
                    pattern = right.encode('utf-8').decode('unicode_escape')
                except Exception:
                    pattern = right
                self._debug(f"[DEBUG] matches检查: '{left_value}' 匹配 '{pattern}'")
                # 使用 fullmatch 确保整个字符串匹配
                try:
                    return bool(re.fullmatch(pattern, left_value))
                except re.error:
                    # 如果正则无效则返回 False
                    return False

            # 解析比较操作
            else:
                # 处理简单的比较操作符
                operators = ['==', '!=', '>', '<', '>=', '<=']
                for op in operators:
                    if op in condition:
                        parts = condition.split(op, 1)
                        left = parts[0].strip()
                        right = parts[1].strip()

                        # 处理左侧值
                        if left.startswith('"') and left.endswith('"'):
                            left_value = left[1:-1]
                        elif left.replace('.', '').isdigit():
                            left_value = float(left) if '.' in left else int(left)
                        else:
                            left_value = self._get_variable_value(left)

                        # 处理右侧值
                        if right.startswith('"') and right.endswith('"'):
                            right_value = right[1:-1]
                        elif right.replace('.', '').isdigit():
                            right_value = float(right) if '.' in right else int(right)
                        else:
                            right_value = self._get_variable_value(right)

                        self._debug(f"[DEBUG] 比较: {left_value} {op} {right_value}")

                        # 执行比较
                        if op == '==':
                            return left_value == right_value
                        elif op == '!=':
                            return left_value != right_value
                        elif op == '>':
                            return left_value > right_value
                        elif op == '<':
                            return left_value < right_value
                        elif op == '>=':
                            return left_value >= right_value
                        elif op == '<=':
                            return left_value <= right_value

                # 如果无法解析，尝试直接评估（简单情况）
                try:
                    result = eval(condition)
                    self._debug(f"[DEBUG] 直接评估结果: {result}")
                    return bool(result)
                except:
                    self._debug(f"[DEBUG] 直接评估失败，返回False")
                    return False

        except Exception as e:
            print(f"❌ 条件评估错误: {e}")
            return False

    def _get_variable_value(self, expr: str):
        """获取变量值或处理表达式"""
        # 如果是变量引用
        if expr.startswith('$'):
            var_name = expr[1:]
            return self.variables.get(var_name, "")
        # 如果是字符串字面量
        elif expr.startswith('"') and expr.endswith('"'):
            return expr[1:-1]
        # 如果是数字
        elif expr.replace('.', '').isdigit():
            return float(expr) if '.' in expr else int(expr)
        else:
            return expr

    def _replace_variables(self, text: str) -> str:
        """替换文本中的变量引用"""
        def replace_var(match):
            var_name = match.group(1)
            # 当请求传入 user_input 参数时，优先返回该值
            if var_name == 'user_input' and hasattr(self, '_last_user_input'):
                return str(self._last_user_input)
            var_value = self.variables.get(var_name, "")
            return str(var_value)

        # 替换 $变量名 格式
        result = re.sub(r'\$(\w+)', replace_var, text)
        return result

    def _process_template(self, text: str) -> str:
        """处理模板字符串中的动态内容"""
        # 处理随机回复
        random_reply_match = re.search(r'{{随机回复:\s*\[(.*?)\]}}', text)
        if random_reply_match:
            options = [opt.strip().strip("'\"") for opt in random_reply_match.group(1).split(',')]
            if options:
                text = text.replace(random_reply_match.group(0), random.choice(options))

        # 处理时间戳
        if '{{时间.时间戳}}' in text:
            text = text.replace('{{时间.时间戳}}', str(int(time.time())))

        # 处理周数
        week_match = re.search(r'{{时间.周数}}', text)
        if week_match:
            week_num = time.strftime("%U")
            text = text.replace('{{时间.周数}}', week_num)

        # 处理随机数
        random_num_match = re.search(r'{{随机数:\s*(\d+)-(\d+)}}', text)
        if random_num_match:
            min_val, max_val = int(random_num_match.group(1)), int(random_num_match.group(2))
            text = text.replace(random_num_match.group(0), str(random.randint(min_val, max_val)))

        return text

    def _safe_eval_expression(self, expr: str):
        """安全地评估只包含字面量和算术运算的表达式。"""
        try:
            node = ast.parse(expr, mode='eval')

            def _eval(node):
                if isinstance(node, ast.Expression):
                    return _eval(node.body)
                if isinstance(node, ast.Constant):
                    return node.value
                if isinstance(node, ast.BinOp):
                    left = _eval(node.left)
                    right = _eval(node.right)
                    if isinstance(node.op, ast.Add):
                        return left + right
                    if isinstance(node.op, ast.Sub):
                        return left - right
                    if isinstance(node.op, ast.Mult):
                        return left * right
                    if isinstance(node.op, ast.Div):
                        return left / right
                    raise ValueError('Unsupported operator')
                if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
                    val = _eval(node.operand)
                    return +val if isinstance(node.op, ast.UAdd) else -val
                # disallow names, calls, etc.
                raise ValueError('Unsupported expression')

            return _eval(node)
        except Exception:
            raise

    def _execute_actions(self, actions, user_input):
        """执行动作序列"""
        responses = []

        # 保存当前用户输入，供变量替换（$user_input）使用
        self._last_user_input = user_input

        for action_type, action_value, condition_stack in actions:
            # 检查条件栈，确定是否执行当前动作
            def _should_execute(cond_stack: List[Tuple[str, str]]) -> bool:
                # 对每个条件条目分别判断：
                # - 'if' 必须为 True 才能继续
                # - 'else' 对应的 if 为 False 时才执行（因此当 if 为 True 时应跳过 else）
                for ct, cexpr in cond_stack:
                    if ct == 'if':
                        if not self._evaluate_condition(cexpr, user_input):
                            return False
                    elif ct == 'else':
                        if self._evaluate_condition(cexpr, user_input):
                            return False
                return True

            if not _should_execute(condition_stack):
                continue

            try:
                if action_type == 'reply':
                    # 处理回复内容中的变量和模板
                    reply_text = self._replace_variables(action_value)
                    reply_text = self._process_template(reply_text)
                    responses.append(reply_text)

                elif action_type == 'log':
                    log_text = self._replace_variables(action_value)
                    log_text = self._process_template(log_text)
                    print(f"📋 [日志] {log_text}")

                elif action_type == 'set':
                    # 解析设置变量操作：set var_name = value
                    if '=' in action_value:
                        var_name, value = action_value.split('=', 1)
                        var_name = var_name.strip().replace('$', '')
                        value = value.strip()

                        # 处理变量引用和表达式
                        # 先替换变量引用（$var -> 值）
                        value_replaced = self._replace_variables(value)

                        # 尝试安全求值（支持数字与字符串的简单算术/拼接）
                        try:
                            eval_result = self._safe_eval_expression(value_replaced)
                            self.variables[var_name] = eval_result
                        except Exception:
                            # 回退：尝试把数字字符串转为数值，否则存原始字符串（去引号）
                            if value_replaced.isdigit():
                                self.variables[var_name] = int(value_replaced)
                            elif value_replaced.replace('.', '', 1).isdigit():
                                self.variables[var_name] = float(value_replaced)
                            else:
                                self.variables[var_name] = value_replaced.strip('"')

                elif action_type == 'call':
                    # 解析函数调用：call result = function_name(params)
                    if '=' in action_value:
                        result_var, func_call = action_value.split('=', 1)
                        result_var = result_var.strip().replace('$', '')
                        func_call = func_call.strip()

                        # 解析函数名与参数，例如: validate_order($user_input)
                        m = re.match(r"^(\w+)\s*\((.*)\)$", func_call)
                        func_name = None
                        args = []
                        if m:
                            func_name = m.group(1)
                            args_str = m.group(2).strip()
                            if args_str:
                                # 简单拆分参数（不处理复杂嵌套或逗号引号情况）
                                parts = [p.strip() for p in args_str.split(',')]
                                for p in parts:
                                    if p.startswith('$'):
                                        # 特殊处理 $user_input，传入当前用户输入
                                        if p == '$user_input':
                                            args.append(user_input)
                                        else:
                                            args.append(self._get_variable_value(p))
                                    elif (p.startswith('"') and p.endswith('"')) or (p.startswith("'") and p.endswith("'")):
                                        args.append(p[1:-1])
                                    elif p.replace('.', '', 1).isdigit():
                                        args.append(float(p) if '.' in p else int(p))
                                    else:
                                        args.append(p)
                        else:
                            # 也可能是无括号形式，如 get_time
                            func_name = func_call

                        # 调用已注册的 Python 回调（优先）
                        result = None
                        if func_name in self.registered_functions:
                            try:
                                result = self.registered_functions[func_name](*args)
                            except Exception as e:
                                print(f"❌ 调用注册函数失败: {e}")
                        else:
                            # 回退到 DSL 中 function 映射或内置实现
                            mapped = self.functions.get(func_name)
                            if mapped:
                                # 映射为模块路径（未实现自动导入），暂时回退到内置行为
                                mapped = mapped.lower()

                            # 内置行为（原有硬编码逻辑）
                            if func_name == 'get_time':
                                result = time.strftime("%Y-%m-%d %H:%M:%S")
                            elif func_name == 'calc_delivery':
                                result = "明天下午"
                            elif func_name == 'validate_order':
                                # 简单示例：以 ORDER 开头视为有效
                                if args and isinstance(args[0], str):
                                    result = args[0].startswith('ORDER')
                                else:
                                    result = False

                        # 赋值回变量域
                        if result is not None:
                            self.variables[result_var] = result

                elif action_type == 'wait_for_input':
                    self.waiting_for = action_value

                elif action_type == 'wait_for_confirm':
                    self.waiting_for = action_value

                elif action_type == 'extract':
                    # 信息提取功能
                    if ' from ' in action_value:
                        var_name, patterns = action_value.split(' from ', 1)
                        var_name = var_name.strip()

                        # 尝试匹配多个模式
                        extracted = None
                        for pattern in patterns.split(' or '):
                            pattern = pattern.strip().strip('"')
                            match = re.search(pattern, user_input)
                            if match:
                                extracted = match.group(1) if match.groups() else match.group(0)
                                break

                        if extracted:
                            self.variables[var_name] = extracted
                            self._debug(f"[DEBUG] 提取到信息: {var_name} = {extracted}")

            except Exception as e:
                print(f"❌ 动作执行错误: {e}")

        return '\n'.join(responses) if responses else None

    def get_intents(self):
        """获取所有可用的意图名称"""
        intents = []
        for scene_name, intents_dict in self.scenes.items():
            intents.extend(intents_dict.keys())
        return intents

    def process(self, intent, user_input):
        """处理意图并生成回复（对外接口保持不变）"""
        # 注意：不要在此处过早清除 `waiting_for`，否则像纯名字这样的直接回复会失去等待状态。
        # 等待状态由具体的意图处理逻辑在处理后清除。

        # 处理特殊等待状态
        if self.waiting_for:
            if self.waiting_for == 'order_number':
                intent = 'provide_order_number'
            elif self.waiting_for == 'return_confirm':
                intent = 'confirm_return'
            elif self.waiting_for == 'issue_description':
                intent = 'describe_issue'
            elif self.waiting_for == 'name':
                intent = 'provide_name'

        # 容错处理：当正在等待姓名（waiting_for == 'name'）且用户直接输入名字（如 "Abe"）
        # 脚本中通常会检测用户是否说了“我叫/我是”等关键词，纯名字输入会无法通过条件分支。
        # 在此我们对这种情况做友好处理——直接将输入保存为 $name 和 $user_name，打印日志并返回成功回复。
        if intent == 'provide_name' and getattr(self, 'waiting_for', None) == 'name':
            # 如果用户没有使用显式关键词，则认为输入是姓名
            if not ("我叫" in user_input or "我是" in user_input):
                name = user_input.strip()
                if name:
                    self.variables['name'] = name
                    self.variables['user_name'] = name
                    # 清除等待状态
                    self.waiting_for = None
                    # 打日志并返回预期回复（尽量与 DSL 中的 reply 保持一致）
                    print(f"📋 [日志] 用户提供姓名：{name}")
                    return f"很高兴认识您，{name}！\n请问有什么可以帮您的？"

        # 在所有场景中查找匹配的意图
        for scene_name, intents_dict in self.scenes.items():
            if intent in intents_dict:
                response = self._execute_actions(intents_dict[intent], user_input)
                if response or not self.waiting_for:
                    return response or "请问您还有其他问题吗？"

        # 没有找到匹配的意图
        return "抱歉，我不太明白您的意思。请换种方式说说看？"

    def get_waiting_status(self):
        """获取当前等待状态（用于外部状态管理）"""
        return self.waiting_for

    def reset_waiting(self):
        """重置等待状态"""
        self.waiting_for = None