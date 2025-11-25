# 增强版客服DSL脚本
# 支持变量、条件、随机回复、函数调用等高级功能

config
    default_scene = "main"
    timeout = 30
    max_retries = 3

var
    user_name = "访客"
    login_count = 0
    last_order = ""
    current_time = ""

function
    get_time = "time_utils.get_current_time"
    calc_delivery = "order_utils.calculate_delivery"
    validate_order = "order_utils.validate_order_id"

scene "main"
    intent "greeting"
        if $login_count == 0
            reply "{{随机回复: ['您好！欢迎首次光临！', '欢迎新朋友！', '很高兴认识您！']}}"
            reply "我是您的AI助手，请问如何称呼您？"
            set user_name = "新用户"
            wait_for_input "name"
        else
            reply "{{随机回复: ['欢迎回来，$user_name！', '您好$user_name，很高兴再次为您服务！', '$user_name，今天有什么可以帮您？']}}"
        end
        set login_count = $login_count + 1
        log "用户问候，登录次数：$login_count"

    intent "provide_name"
        condition $user_input contains "我叫" or $user_input contains "我是"
            extract name from "我叫(.*)" or "我是(.*)"
            set user_name = $name
            reply "很高兴认识您，$name！"
            reply "请问有什么可以帮您的？"
        end
        log "用户提供姓名：$user_name"

scene "time_service"
    intent "ask_time"
        call current_time = get_time()
        reply "当前时间是：$current_time"
        reply "{{随机回复: ['请问还需要其他帮助吗？', '还有什么可以为您服务的？', '希望您有美好的一天！']}}"
        log "时间查询：$current_time"

    intent "ask_date"
        call current_time = get_time()
        reply "今天是：$current_time"
        reply "本周是今年的第{{时间.周数}}周"
        log "日期查询"

scene "order_management"
    intent "check_order"
        reply "正在查询订单信息..."

        condition $last_order != ""
            reply "为您查询最近订单：$last_order"
            reply "状态：已发货，预计明天送达"
        else
            reply "请问您要查询哪个订单号？"
            wait_for_input "order_number"
        end

        log "订单查询请求"

    intent "provide_order_number"
        condition $user_input matches "ORDER\d+"
            set last_order = $user_input
            call is_valid = validate_order($user_input)

            if $is_valid
                reply "订单 $user_input 验证成功！"
                reply "订单状态：已发货"
                call delivery_date = calc_delivery($user_input)
                reply "预计送达时间：$delivery_date"
            else
                reply "订单号 $user_input 无效或不存在"
            end
        else
            reply "订单号格式不正确，请提供类似 ORDER123 的格式"
        end
        log "订单号处理：$user_input"

    intent "return_request"
        reply "了解您要退货的需求"

        condition $last_order != ""
            reply "检测到您最近的订单：$last_order"
            reply "是否为此订单申请退货？"
            wait_for_confirm "return_confirm"
        else
            reply "请提供需要退货的订单号"
            wait_for_input "return_order"
        end

        log "退货申请开始"

    intent "confirm_return"
        reply "已为您提交订单 $last_order 的退货申请"
        reply "客服将在24小时内联系您处理后续事宜"
        reply "退货编号：RET{{时间.时间戳}}"
        log "退货确认完成"

scene "customer_support"
    intent "complaint"
        reply "抱歉给您带来不便"
        reply "请简要描述您遇到的问题："
        wait_for_input "issue_description"
        log "用户投诉受理"

    intent "describe_issue"
        reply "感谢您的反馈，我们已经记录：$user_input"
        reply "客服专员将尽快联系您处理"
        reply "紧急问题可拨打热线：400-123-4567"
        log "问题描述记录：$user_input"

    intent "ask_human_agent"
        reply "正在为您转接人工客服..."
        reply "当前排队人数：{{随机数: 1-5}}人"
        reply "预计等待时间：{{随机数: 2-10}}分钟"
        log "请求人工客服"

scene "fallback"
    intent "unknown"
        reply "抱歉，我没有完全理解您的意思"
        reply "您可以尝试以下方式："
        reply "1. 查询订单状态"
        reply "2. 申请退货"
        reply "3. 联系人工客服"
        reply "请问您需要哪项服务？"
        log "未知意图处理：$user_input"

    intent "thankyou"
        reply "{{随机回复: ['不客气！', '很高兴能帮到您！', '这是我应该做的！']}}"
        reply "祝您生活愉快！"
        log "用户致谢"

# 系统指令
scene "system"
    intent "reset"
        reply "系统已重置"
        set user_name = "访客"
        set login_count = 0
        set last_order = ""
        log "系统重置操作"

    intent "help"
        reply "=== 可用功能 ==="
        reply "📅 时间查询 - 询问当前时间日期"
        reply "📦 订单管理 - 查询订单、退货申请"
        reply "👥 人工客服 - 转接人工服务"
        reply "🔄 系统重置 - 清除当前会话数据"
        reply "❓ 帮助信息 - 显示本提示"
        log "用户请求帮助"