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
    set global_status = ""
    log "用户问候，状态：$global_status"

intent "check_order"
    reply "正在查询订单信息..."
    set global_status = "check_order"
    reply "请问您要查询哪个订单号？"
    log "订单查询请求，状态：$global_status"

intent "provide_order_number"
    if $user_input matches "ORDER\\d+"
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