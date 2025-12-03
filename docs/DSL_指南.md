# DSL编写指南

## 1. 概述

DSL（Domain Specific Language）脚本语言是专门为客服机器人场景设计的领域特定语言。通过编写DSL脚本，您可以定义客服机器人的对话流程、业务逻辑和应答规则，无需修改代码即可实现复杂的客服功能。

### 主要特性

- **声明式语法**：直观易懂，类似自然语言
- **模块化设计**：支持配置、变量、意图分离
- **灵活扩展**：支持自定义函数和条件逻辑
- **AI集成**：与LLM无缝结合实现智能意图识别

## 2. 基础语法结构

### 2.1 脚本文件结构

```
var
    # 变量声明

intent "意图名称"
    # 业务逻辑语句
```

### 2.2 注释

使用 `#`符号添加注释：

```
# 这是单行注释
```

## 3. 变量区块 (var)

变量区块用于声明和初始化业务变量，支持全局作用域。

### 语法格式

```
var
    变量名 = 初始值
```

### 示例

```
var
    login_count = 0            # 登录次数计数器
    last_order = ""            # 最后操作的订单
    global_status = ""         # 全局状态标识
    user_level = "normal"      # 用户等级
    retry_count = 0            # 重试计数
```

### 变量命名规则

- 以字母或下划线开头
- 可包含字母、数字、下划线
- 区分大小写
- 示例：`user_name`, `order_count`, `_temp`

## 4. 意图区块 (intent)

意图区块是核心业务逻辑单元，每个意图对应一种用户需求场景。

### 语法格式

```
intent "意图名称"
    语句1
    语句2
    ...
```

### 示例

```
intent "greeting"
    reply "您好！欢迎光临！"
    reply "请问有什么可以帮您？"
    set global_status = ""
```

意图名称需要起得有意义，以便大模型识别。

## 5. 语句类型

### 5.1 回复语句 (reply)

向用户发送文本消息。

```
reply "消息内容"
```

**示例：**

```
reply "订单查询成功！"
reply "您的订单号是：$order_id"
```

### 5.2 赋值语句 (set)

设置变量值，支持表达式运算。

```
set 变量名 = 表达式
```

**示例：**

```
set login_count = $login_count + 1
set full_name = "张" + "三"
set total_price = $price * $quantity
```

### 5.3 函数调用语句 (call)

调用内置或自定义函数处理数据。

```
call 结果变量 = 函数名(参数)
```

**示例：**

```
call order_id = extract_order_number($user_input)
call delivery_date = calc_delivery($order_id)
```

### 5.4 条件语句 (if/else)

根据条件执行不同的逻辑分支。

```
if 条件表达式
    # then分支
else
    # else分支
end
```

**示例：**

```
if $order_id == "未找到订单号"
    reply "请提供有效订单号"
else
    reply "订单验证成功"
end
```

### 5.5 日志语句 (log)

记录运行日志到文件系统。

```
log "日志内容"
```

**示例：**

```
log "用户查询订单：$order_id"
log "退货申请提交：$last_order"
```

## 6. 表达式和运算符

### 6.1 字面量

```
"字符串值"      # 字符串
123            # 整数
45.67          # 浮点数
true/false     # 布尔值
```

### 6.2 变量引用

使用 `$变量名`格式引用变量：

```
$user_input     # 用户输入内容
$last_order     # 最后订单号
$global_status  # 全局状态
```

### 6.3 算术运算符

```
a + b    # 加法（数字相加或字符串连接）
a - b    # 减法
a * b    # 乘法
a / b    # 除法
```

### 6.4 比较运算符

```
a == b   # 等于
```

## 7. 内置函数

### 7.1 extract_order_number(text)

从文本中提取订单号。

**参数：**

- `text`：输入文本（可选，默认为用户输入）

**返回：** 提取的订单号或"未找到订单号"

**示例：**

```
call order_id = extract_order_number($user_input)
# 输入："我的订单是ORDER123" → 返回："ORDER123"
```

### 7.2 calc_delivery(order_id)

计算订单配送时间。

**参数：**

- `order_id`：订单号

**返回：** 配送时间或错误信息

**示例：**

```
call delivery_date = calc_delivery($order_id)
# 输入："ORDER123" → 返回："2024-01-15"
```

## 8. 完整示例脚本

### 8.1 基础客服机器人

```
var
    login_count = 0
    last_order = ""
    global_status = ""

intent "greeting"
    reply "您好！欢迎使用客服系统！"
    reply "请问您需要什么帮助？"
    set global_status = ""

intent "check_order"
    reply "正在查询订单信息..."
    set global_status = "check_order"
    reply "请提供您的订单号："

intent "provide_order_number"
    call order_id = extract_order_number($user_input)
    
    if $order_id == "未找到订单号"
        reply "未识别到订单号，请确认格式（如：ORDER123）"
    else
        call delivery_date = calc_delivery($order_id)
        
        if $delivery_date == "订单未找到"
            reply "订单 $order_id 不存在，请检查订单号"
        else
            set last_order = $order_id
            reply "订单 $order_id 查询成功！"
            reply "预计发货时间：$delivery_date"
        end
    end

intent "help"
    reply "=== 帮助信息 ==="
    reply "1. 查询订单 - 提供订单号查询状态"
    reply "2. 人工客服 - 转接人工服务"
    reply "3. 帮助 - 显示本提示"
```

### 8.2 进阶电商客服

```
var
    current_order = ""
    user_tier = "standard"
    service_type = ""
    complaint_count = 0

intent "welcome"
    reply "欢迎来到$company_name客服中心！"
    reply "我们提供订单查询、退货申请、投诉建议等服务"
    set service_type = ""

intent "order_inquiry"
    set service_type = "order_inquiry"
    reply "请提供订单号，格式如：ORDER20240001"
    
intent "process_order"
    call order_num = extract_order_number($user_input)
    
    if $order_num == "未找到订单号"
        reply "订单号格式错误，请重新输入"
    else
        set current_order = $order_num
        call status = get_order_status($order_num)
        call delivery = get_delivery_info($order_num)
        
        reply "订单号：$order_num"
        reply "当前状态：$status"
        reply "物流信息：$delivery"
        
        if $status == "已发货"
            reply "您的订单已在途中，预计3天内送达"
        else if $status == "待发货"
            reply "我们将尽快为您安排发货"
        end
    end

intent "return_request"
    if $current_order == ""
        reply "请先提供需要退货的订单号"
    else
        set service_type = "return"
        reply "确认要为订单 $current_order 申请退货吗？"
        reply "回复'确认'继续退货流程"
    end

intent "confirm_return"
    if $service_type == "return"
        reply "已提交订单 $current_order 的退货申请"
        reply "退货专员将在24小时内联系您"
        log "退货申请：$current_order"
        set service_type = ""
    else
        reply "请先开始退货流程"
    end
```

## 9. 最佳实践

### 9.1 命名规范

- **意图名称**：使用动词+名词，如 `query_order`, `apply_return`
- **变量名**：使用有意义的英文，如 `user_level`, `order_status`
- **配置项**：使用小写+下划线，如 `max_retries`, `default_timeout`

### 9.2 错误处理

```
intent "process_input"
    call result = some_function($input)
    
    if $result == "error"
        reply "处理过程中出现错误，请稍后重试"
        log "函数执行错误：输入=$input"
    else
        # 正常处理逻辑
    end
```

### 9.3 状态管理

```
# 使用全局状态跟踪对话流程
set service_type = "order_query"
set current_step = "waiting_order_number"

# 根据状态提供不同的错误提示
if $service_type == "order_query" and $current_step == "waiting_order_number"
    reply "请提供订单号继续查询"
end
```

### 9.4 模块化设计

```
# 通用回复模板
intent "show_help"
    if $service_type == "order"
        reply "=== 订单帮助 ==="
        reply "请输入订单号查询状态"
    else if $service_type == "return"
        reply "=== 退货帮助 ==="
        reply "请确认订单号或联系人工客服"
    else
        reply "=== 通用帮助 ==="
        reply "输入'订单'查询，'退货'申请退货"
    end
```

## 10. 调试技巧

### 10.1 日志调试

```
# 在关键位置添加日志
log "进入意图：provide_order_number"
log "用户输入：$user_input"
log "提取的订单号：$order_id"
```

### 10.2 变量检查

```
# 临时添加回复显示变量值
reply "[调试] 当前订单：$current_order"
reply "[调试] 服务类型：$service_type"
```

### 10.3 分段测试

```
# 注释掉部分代码进行测试
intent "test"
    reply "测试消息"
    # set var = value  # 暂时注释
    # call result = function()  # 暂时注释
```

## 11. 常见问题解答

### Q: 变量引用不生效？

A: 确保变量名前有`$`符号，且变量已在var区块声明。

### Q: 条件判断总是失败？

A: 检查比较运算符两边的数据类型是否匹配，字符串比较使用双引号。

### Q: 函数调用返回意外结果？

A: 检查函数参数格式，使用log语句记录输入输出。

### Q: 脚本解析错误？

A: 检查语法格式，确保区块和语句的正确嵌套。

------

**附录：DSL语法速查表**

| 语法元素 | 示例                 | 说明           |
| -------- | -------------------- | -------------- |
| 变量声明 | `var count=0`        | 业务变量       |
| 意图定义 | `intent "greeting"`  | 业务场景       |
| 回复消息 | `reply "Hello"`      | 向用户发送消息 |
| 变量赋值 | `set count=$count+1` | 修改变量值     |
| 函数调用 | `call id=extract()`  | 调用处理函数   |
| 条件判断 | `if $a==$b`          | 条件分支       |
| 日志记录 | `log "message"`      | 记录运行日志   |

本指南将随着DSL功能的扩展持续更新。如有问题，请参考示例脚本或联系开发团队。