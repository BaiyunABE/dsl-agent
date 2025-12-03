step "greeting"
    reply "您好！欢迎光临！"
    reply "请问有什么可以帮您？"
    wait "greeting" "return_request" "return_request" "complaint" "ask_human_agent" "thankyou" "unknown"

step "return_request"
    reply "了解您要退货的需求"
    reply "请提供需要退货的订单号"
    wait "provide_order_number"

step "provide_order_number"
    reply "已为您提交订单" + $user_input + "的退货申请"
    reply "客服将在24小时内联系您处理后续事宜"
    log "退货申请：" + $user_input
    wait "greeting" "return_request" "return_request" "complaint" "ask_human_agent" "thankyou" "unknown"

step "complaint"
    reply "抱歉给您带来不便"
    reply "请简要描述您遇到的问题："
    wait "describe_issue"

step "describe_issue"
    reply "感谢您的反馈，我们已经记录"
    reply "客服专员将尽快联系您处理"
    reply "紧急问题可拨打热线：400-123-4567"
    log "用户投诉：" + $user_input
    wait "greeting" "return_request" "return_request" "complaint" "ask_human_agent" "thankyou" "unknown"

step "ask_human_agent"
    reply "收到，稍候会有人工客服与您联系"
    log "请求人工客服"
    wait "greeting" "return_request" "return_request" "complaint" "ask_human_agent" "thankyou" "unknown"

step "unknown"
    reply "抱歉，我没有完全理解您的意思"
    reply "您可以尝试以下方式："
    reply "1. 申请退货"
    reply "2. 投诉"
    reply "3. 联系人工客服"
    reply "请问您需要哪项服务？"
    wait "greeting" "return_request" "return_request" "complaint" "ask_human_agent" "thankyou" "unknown"

step "thankyou"
    reply "不客气！"
    reply "祝您生活愉快！"
    wait "greeting" "return_request" "return_request" "complaint" "ask_human_agent" "thankyou" "unknown"