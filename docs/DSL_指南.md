# DSL 使用指南

版本：1.0

日期：2025-11-25

概述
----
本指南面向使用或扩展 `dsl-agent` 项目的开发者与测试人员，说明 DSL（领域专用语言）的语法、指令语义、变量与模板用法，并提供常见示例与调试技巧。

目录
----
- 设计理念
- 文件结构
- 语法元素详解
  - 配置与变量
  - 函数映射
  - 场景（scene）与意图（intent）
  - 动作（actions）
  - 条件表达式
  - 模板与内置占位符
- 典型示例
- 扩展与调试
- 常见问题（FAQ）

设计理念
----
DSL 目标是用简明、可读的脚本描述客服机器人多轮对话与应答逻辑。语言应当支持：
- 场景/意图分层组织
- 可执行动作（回复、日志、变量赋值、函数调用、等待输入）
- 条件判断与分支
- 简易模板与变量替换
- 可扩展的函数调用（注册 Python 回调）

文件结构
----
一个 DSL 文件包含若干区块（顺序不限）：
- `config`：可选，放置运行时配置项
- `var`：可选，声明初始变量
- `function`：可选，映射到外部函数标识
- `scene "name"`：场景定义，包含若干 `intent`

整体示例结构：

scene "main"
    intent "greeting"
        reply "你好，欢迎！"
        wait_for_input "name"

语法元素详解
----

1) 配置与变量
- config
    - 语法：`config` 后缩进写 `key = value`
    - 示例：
      config
          default_scene = "main"
          timeout = 30

- var
    - 语法：`var` 后缩进写 `name = value`
    - 支持数字和字符串（字符串用双引号或单引号）
    - 示例：
      var
          user_name = "访客"
          login_count = 0

2) 函数映射
- function
    - 用于把 DSL 中的函数名映射到外部实现（字符串形式），或作为占位符。
    - 示例：
      function
          get_time = "time_utils.get_current_time"

- 注册 Python 回调
    - 在代码中可以通过 `DSLEngine.register_function(name, callable)` 注册实际实现，`call` 优先会调用 `registered_functions`。

3) 场景与意图
- 定义 `scene "name"`，在其内部使用 `intent "intent_name"`。
- 每个 `intent` 下按顺序写动作（actions）。

示例：
scene "order_management"
    intent "check_order"
        reply "正在查询订单..."

4) 动作（actions）
支持的动作类型：
- `reply "text"`：向用户回复一条文本。文本支持变量替换（`$var`）与模板（见后）。
- `log "text"`：打印日志（用于调试/记录）。
- `set var = expr`：设置变量，expr 支持数字、字符串、简单算术表达式与变量引用（如 `$login_count + 1`）。
- `call result = func(args)`：调用函数并把返回值赋给变量。参数支持 `$user_input`、变量、字面量。若函数在 `registered_functions` 注册，会优先调用。
- `wait_for_input "type"`：设置等待状态，下一条输入可映射为特定 intent（见引擎映射规则）。
- `wait_for_confirm "type"`：类似确认类型的等待。
- `extract var from "pattern" or "pattern2"`：按正则从用户输入提取信息并写入变量。

示例：
intent "provide_order_number"
    condition $user_input matches "ORDER\\d+"
        set last_order = $user_input
        call is_valid = validate_order($user_input)
        if $is_valid
            reply "订单 $user_input 验证成功"
        else
            reply "订单号无效"
        end

5) 条件表达式
支持三类条件：
- contains：子串包含，如 `$user_input contains "我叫"`
- matches：正则匹配，如 `$user_input matches "ORDER\\d+"`（注意脚本中需要双反斜杠转义）
- 比较操作：`==, !=, >, <, >=, <=`，左右可以是 `$var`、数字或字符串字面量

条件格式举例：
if $login_count == 0
    reply "欢迎新用户"
else
    reply "欢迎回来"
end

6) 模板与内置占位符
- 变量替换：在 reply 文本中使用 `$var` 会被替换为当前变量值（例如 `$user_name`）。
- 随机回复：`{{随机回复: ['A', 'B', 'C']}}` 随机选择一项替换。
- 时间戳：`{{时间.时间戳}}` 替换为 Unix 时间戳整数。
- 周数：`{{时间.周数}}` 替换为当前周数（字符串格式）。
- 随机数：`{{随机数: min-max}}` 生成区间内随机整数。

示例：
reply "{{随机回复: ['您好！', '欢迎！']}} $user_name"

典型示例
----

1) 新用户问候示例：

scene "main"
    intent "greeting"
        if $login_count == 0
            reply "{{随机回复: ['您好！欢迎首次光临！','欢迎新朋友！']}}"
            reply "请问如何称呼您？"
            wait_for_input "name"
        else
            reply "欢迎回来，$user_name！"
        end

2) 订单号提取与校验：

intent "provide_order_number"
    condition $user_input matches "ORDER\\d+"
        set last_order = $user_input
        call is_valid = validate_order($user_input)
        if $is_valid
            reply "订单 $user_input 验证成功！"
        else
            reply "订单号无效"
        end
    else
        reply "订单号格式不正确，请提供类似 ORDER123"
    end

扩展与调试
----

- 注册 Python 回调：在 `main.py` 或测试中使用 `dsl_engine.register_function('name', fn)` 将外部逻辑注入 DSL。
- 调试：在 `DSLEngine` 实例化时传入 `debug=True`，会打印条件评估等调试信息。
- 常见问题排查：
  - 正则匹配失败：检查脚本中是否对反斜杠进行了正确转义（`\\d` 表示正则 `\d`）。
  - 变量未替换：确认变量名拼写一致且已在 `var` 中初始化或通过 `set` 赋值。
  - LLM 识别为 `unknown`：检查 `LLMClient` 是否使用真实 LLM，或检查关键词回退表是否包含相关关键词。

常见问题（FAQ）
----
Q：如何让脚本调用外部 API？
A：在 Python 代码中实现函数并通过 `register_function` 注册，然后在脚本中使用 `call result = my_func($user_input)`。

Q：如何增加新的模板占位符？
A：编辑 `dsl_engine._process_template()` 并实现新的占位符解析逻辑。

Q：脚本中字符串如何包含引号？
A：尽量避免复杂嵌套；当前解析器对嵌套引号支持有限。若必须，考虑在详设计中改用更健壮的解析器（如 `lark`）。

结语
----
本指南为简洁版手册，覆盖常用指令与用法。若需要更正式的语言规范（BNF）、完整示例集合或工具（语法高亮、lint），可以继续扩展为 `docs/DSL_SPEC.md` 和示例库。我可以继续为你生成更完整的语言规范与示例集。