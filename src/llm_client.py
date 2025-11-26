"""
LLM意图识别模块
连接大模型API进行意图分类
"""

import os
from openai import OpenAI

class LLMClient:
    def __init__(self, api_key=None, debug=False):
        """LLM 客户端。

        - If `api_key` is None, read from env `DSL_AGENT_API_KEY`.
        - `debug` controls whether debug prints are emitted.
        """
        self.debug = debug

        # Resolve API key: explicit -> env
        resolved_key = api_key or os.environ.get('DSL_AGENT_API_KEY')

        # Model and base URL can be configured via environment variables
        self.model = os.environ.get('DSL_AGENT_MODEL', 'doubao-seed-1-6-251015')
        base_url = os.environ.get('DSL_AGENT_BASE_URL', 'https://ark.cn-beijing.volces.com/api/v3')

        self.api_key = resolved_key
        self.client = None

        # Initialize OpenAI-compatible client if enabled and API key is provided

        if self.debug:
            masked = self._mask_key(self.api_key)
            print(f"[DEBUG] 初始化LLM客户端，使用API: {masked}")
        try:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=base_url
            )
            if self.debug:
                print("[DEBUG] LLM客户端初始化完成")
        except Exception as e:
            print(f"[ERROR] 初始化LLM客户端失败: {e}. ")
            self.client = None

    def recognize_intent(self, user_input, available_intents):
        """识别用户输入的意图"""
        if self.debug:
            print(f"[DEBUG] 开始意图识别")
            print(f"[DEBUG] 用户输入: '{user_input}'")
            print(f"[DEBUG] 可用意图: {available_intents}")

        result = self._llm_recognize_intent(user_input, available_intents)

        if self.debug:
            print(f"[DEBUG] 意图识别完成: {result}")
        return result

    def _llm_recognize_intent(self, user_input, available_intents):
        """使用DeepSeek LLM API进行意图识别"""
        try:
            prompt = f"""请从以下意图列表中分类用户输入，只返回意图名称，不要返回其他内容。

可用意图：{', '.join(available_intents)}
用户输入：{user_input}

请直接返回最匹配的意图名称"""

            if self.debug:
                print(f"[DEBUG] 构造的提示词: {prompt[:200]}...")  # 只显示前200字符避免过长
                print("[DEBUG] 调用LLM API...")
            response = self.client.chat.completions.create(
                model="doubao-seed-1-6-251015",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,
                max_tokens=10,
                stream=False
            )

            intent = response.choices[0].message.content.strip()
            if self.debug:
                print(f"[DEBUG] LLM原始响应: '{intent}'")

            # 验证返回的意图是否在可用列表中
            if intent in available_intents:
                if self.debug:
                    print(f"[DEBUG] 意图验证通过: '{intent}' 在可用意图列表中")
                return intent
            else:
                if self.debug:
                    print(f"[DEBUG] 意图验证失败: '{intent}' 不在可用意图列表中，返回'unknown'")
                return 'unknown'

        except Exception as e:
            print(f"[ERROR] LLM API调用失败: {e}")
            if self.debug:
                print("[DEBUG] 切换到备用关键词匹配方案")
            return 'unknown'

    def _mask_key(self, key: str) -> str:
        """Mask an API key for logs, showing only first 4 and last 4 chars when possible."""
        if not key:
            return "(no-key)"
        if len(key) <= 8:
            return "*" * (len(key) - 2) + key[-2:]
        return key[:4] + "..." + key[-4:]

# 使用示例
if __name__ == "__main__":
    print("=== LLM意图识别模块测试 ===")

    # 默认使用LLM API
    print("\n1. 测试LLM API模式:")
    client = LLMClient(debug=True)

    test_input = "你好，我想查询我的订单状态"
    available_intents = ['greeting', 'ask_time', 'check_order', 'return_request', 'complaint']

    print(f"\n[TEST] 测试输入: '{test_input}'")
    intent = client.recognize_intent(test_input, available_intents)
    print(f"\n[RESULT] 最终识别结果: {intent}")