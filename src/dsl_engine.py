"""
dsl_engine.py -
基于语法分析器的解释执行引擎
"""

import datetime
import os
from typing import Dict, Any, List, Optional
from llm_client import LLMClient

class DSLEngine:
    def __init__(self, script_file: str = None, script_content: str = None, debug: bool = False):
        """
        初始化DSL引擎
        """
        self.debug = debug
        self.ast = None
        self.variables = {
            'user_input': '',
            'input_history': []
        }
        self.current_step = None
        self.input_history = []
        
        self.llm_client = LLMClient(debug=debug)

        # 加载脚本
        if script_file:
            self._load_script_from_file(script_file)
        elif script_content:
            self._load_script_from_content(script_content)
        else:
            raise ValueError("必须提供script_file或script_content参数")

    def _debug(self, msg: str):
        """调试信息输出"""
        if self.debug:
            print(f"[DEBUG] {msg}")

    def _load_script_from_file(self, script_file: str):
        """从文件加载脚本"""
        if not os.path.isabs(script_file):
            base_dir = os.path.dirname(__file__)
            self.script_file = os.path.join(base_dir, script_file)
        else:
            self.script_file = script_file
        
        try:
            with open(self.script_file, 'r', encoding='utf-8') as f:
                script_content = f.read()
            self._parse_script(script_content)
        except FileNotFoundError:
            raise Exception(f"脚本文件不存在: {self.script_file}")

    def _load_script_from_content(self, script_content: str):
        """从内容加载脚本"""
        self.script_file = None
        self._parse_script(script_content)

    def _parse_script(self, script_content: str):
        """解析脚本内容"""
        try:
            from parser import Parser
            parser = Parser(debug=self.debug)
            self.ast = parser.parse(script_content)
            
            if not self.ast:
                raise Exception("脚本解析失败")
            
            self._debug("脚本解析成功")
            
        except Exception as e:
            raise Exception(f"脚本解析失败: {e}")

    def _evaluate_expression(self, node: Dict) -> Any:
        """评估表达式节点"""
        if not isinstance(node, dict):
            return str(node)

        node_type = node.get('type', '')
        
        if node_type == 'String':
            return node.get('value', '')
        elif node_type == 'Variable':
            var_name = node.get('value', '')[1:]  # 去掉$前缀
            return self.variables.get(var_name, '')
        elif node_type == 'Arithmetic':
            return self._evaluate_arithmetic(node)
        else:
            return ''

    def _evaluate_arithmetic(self, node: Dict) -> Any:
        """评估算术表达式"""
        if not node.get('children') or len(node['children']) != 2:
            return ""
        
        left = self._evaluate_expression(node['children'][0])
        right = self._evaluate_expression(node['children'][1])
        operator = node.get('value', '+')
        
        if operator == '+':
            return str(left) + str(right)
        return ""

    def _execute_statement(self, statement: Dict, user_input: str = '') -> List[str]:
        """执行单个语句"""
        responses = []
        node_type = statement.get('type', '')
        
        # 更新用户输入变量
        self.variables['user_input'] = user_input
        if user_input:
            self.input_history.append(user_input)
            self.variables['input_history'] = self.input_history
        
        if node_type == 'Reply':
            expression = statement.get('value')
            if expression:
                reply_text = self._evaluate_expression(expression)
                responses.append(reply_text)
                
        elif node_type == 'Log':
            expression = statement.get('value')
            if expression:
                log_text = self._evaluate_expression(expression)
                self._write_log(log_text)
                
        elif node_type == 'Wait':
            responses.extend(self._execute_wait_statement(statement, user_input))
                
        return responses

    def _write_log(self, log_text: str):
        """写入日志文件"""
        log_file_path = "dsl_engine.log" if not self.script_file else self.script_file + '.log'
        
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {log_text}\n"
        
        try:
            with open(log_file_path, 'a', encoding='utf-8') as log_file:
                log_file.write(log_entry)
            self._debug(f"日志写入成功: {log_text}")
        except Exception as e:
            print(f"❌ 写入日志文件失败: {e}")
    
    def _wait_for_user_input(self, prompt: str = "请输入: ") -> str:
        """等待用户输入"""
        return input(prompt).strip()
    
    def _intent_recognition(self, user_input: str) -> str:
        """使用LLM进行意图识别"""
        intent = self.llm_client.recognize_intent(
            user_input, 
            self.get_steps()
        )
        self._debug(f"识别到的意图: {intent}")
        return intent
    
    def _execute_wait_statement(self, wait_statement: Dict, current_user_input: str) -> List[str]:
        """执行 wait 语句（阻塞等待用户输入）"""
        responses = []
        
        # 获取意图列表
        intents = wait_statement.get('value', [])
        
        if not intents:
            return []
        
        # 等待用户输入
        while True:
            try:
                user_input = input("👤: ").strip()
                
                if user_input.lower() in ['退出', 'quit', 'exit', 'bye']:
                    print("🤖: 感谢使用，再见！")
                    exit(0)
                
                if not user_input:
                    continue
                
                # 使用LLM识别用户输入属于哪个意图
                matched_intent = self._recognize_intent_from_list(user_input, intents, responses)
                
                # 决定跳转到哪个步骤
                if matched_intent and matched_intent in self.get_steps():
                    next_step = matched_intent
                else:
                    # 如果没有匹配的意图，使用第一个意图作为默认
                    next_step = intents[0]
                self._debug(f"跳转到步骤: {next_step}")
                
                # 执行跳转到下一步
                response = self.process(next_step, user_input)
                if response:
                    responses.append(response)
                
                break  # 处理完一次输入后退出循环
                
            except KeyboardInterrupt:
                print("\n🤖: 感谢使用，再见！")
                exit(0)
            except Exception as e:
                if self.debug:
                    import traceback
                    traceback.print_exc()
                print(f"🤖: 系统出现错误: {e}")
                continue
        
        return responses
    
    def _recognize_intent_from_list(self, user_input: str, intents: List[str], responses: List[str]) -> str:
        """从意图列表中识别用户输入属于哪个意图"""
        if not intents:
            return ""
        
        # 使用LLM进行意图识别
        matched_intent = self.llm_client.recognize_intent(user_input, intents, responses)
        self._debug(f"用户输入: '{user_input}' 匹配到的意图: {matched_intent}")
        return matched_intent

    def get_steps(self) -> List[str]:
        """获取所有可用的步骤名称"""
        steps = []
        if not self.ast:
            return steps
        
        # 处理不同的AST结构
        if 'children' in self.ast:
            # 标准结构
            sections = self.ast['children']
        else:
            # 简化模式结构
            return ["greeting", "farewell", "help", "thanks", "unknown"]
        
        for section in sections:
            if isinstance(section, dict) and section.get('type') == 'Step':
                step_name = section.get('value', '')
                if step_name:
                    steps.append(step_name)
        
        return steps

    def process(self, step_name: str, user_input: str = '') -> str:
        """处理步骤并生成回复"""
        self._debug(f"处理步骤: {step_name}, 输入: {user_input}")
        
        # 查找匹配的步骤
        target_step = None
        if self.ast and 'children' in self.ast:
            for section in self.ast['children']:
                if section['type'] == 'Step' and section.get('value') == step_name:
                    target_step = section
                    break
        
        if not target_step:
            available_steps = self.get_steps()
            return f"未知步骤: {step_name}。可用步骤: {', '.join(available_steps)}"
        
        # 设置当前步骤
        self.current_step = step_name
        
        # 执行步骤中的语句
        responses = []
        statements = target_step.get('children', [])
        
        for statement in statements:
            node_type = statement.get('type', '')
            
            if node_type == 'Wait':
                # 对于wait语句，先输出之前的回复
                if responses:
                    print(f"🤖: {'\n'.join(responses)}")
                    responses = []  # 清空已输出的回复
                
                # 执行wait语句（会阻塞等待用户输入）
                wait_responses = self._execute_wait_statement(statement, user_input)
                responses.extend(wait_responses)
            else:
                # 其他语句正常执行
                responses.extend(self._execute_statement(statement, user_input))
        
        return '\n'.join(responses) if responses else ""

    def get_variables(self) -> Dict[str, Any]:
        """获取当前变量状态"""
        return self.variables.copy()

    def get_current_step(self) -> Optional[str]:
        """获取当前步骤"""
        return self.current_step
    
    def start(self, initial_step: str = "greeting", initial_input: str = ""):
        """启动机器人交互循环"""
        # 直接从初始步骤开始处理
        response = self.process(initial_step, initial_input)
        if response:
            print(f"🤖: {response}")