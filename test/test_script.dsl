# 测试用DSL脚本
var
    default_response = "抱歉，我无法处理您的请求"
    order_number = ""
    delivery_time = "未知"
    user_input = ""

intent "greeting"
    reply "您好！我是客服机器人，请问有什么可以帮您？"
    log "用户打招呼"

intent "provide_order_number"
    reply "已收到您的订单号：$order_number"
    set order_number = $user_input
    call delivery_time = calc_delivery($order_number)
    
    if $delivery_time == "未知"
        reply "未找到该订单的发货信息"
    else
        reply "预计发货时间：$delivery_time"
    end
    log "查询订单 $order_number 的发货时间"

intent "ask_delivery_time"
    if $order_number == ""
        reply "请先提供您的订单号"
    else
        call delivery_time = calc_delivery($order_number)
        reply "订单 $order_number 的预计发货时间：$delivery_time"
    end

intent "help"
    reply "我可以帮您：1. 查询订单状态 2. 查询发货时间 3. 提供客服帮助"
    log "用户请求帮助"

intent "exit"
    reply "感谢使用，再见！"
    log "用户退出对话"