"""
解析器测试桩
"""
class MockParser:
    def __init__(self, debug=False):
        self.debug = debug
        self.ast = None
    
    def parse(self, script_content):
        if self.debug:
            print(f"[MOCK] 解析脚本内容: {script_content[:50]}...")
        
        # 简单的模拟AST
        if "step greeting" in script_content:
            self.ast = {
                'type': 'Script',
                'children': [
                    {
                        'type': 'Step',
                        'value': 'greeting',
                        'children': [
                            {
                                'type': 'Reply',
                                'value': {'type': 'String', 'value': '你好！我是客服机器人。'}
                            }
                        ]
                    }
                ]
            }
        elif "invalid" in script_content:
            raise Exception("模拟解析错误")
        
        return self.ast