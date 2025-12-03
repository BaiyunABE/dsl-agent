# 酒店预订客服机器人
var
    default_response = "您好，我是酒店预订助手，请问有什么可以帮您？"
    customer_name = ""
    checkin_date = ""
    checkout_date = ""
    room_type = ""
    guest_count = 2
    total_price = 0
    booking_reference = ""
    current_step = "welcome"

intent "welcome"
    reply "🏨 欢迎使用酒店预订系统！"
    reply "我可以帮您：查询房型、预订房间、修改订单、查询价格"
    set current_step = "main_menu"

intent "ask_room_types"
    reply "我们提供以下房型："
    reply "1. 标准大床房 - ￥399/晚"
    reply "2. 豪华双床房 - ￥499/晚" 
    reply "3. 行政套房 - ￥899/晚"
    reply "4. 总统套房 - ￥1599/晚"
    log "用户查询房型信息"

intent "provide_checkin_date"
    set checkin_date = $user_input
    call date_valid = validate_date($checkin_date)
    
    if $date_valid == true
        reply "✅ 入住日期已记录：$checkin_date"
        set current_step = "get_checkout_date"
        reply "请告诉我离店日期（格式：YYYY-MM-DD）"
    else
        reply "❌ 日期格式不正确，请使用 YYYY-MM-DD 格式"
    end
    log "用户提供入住日期：$checkin_date"

intent "provide_checkout_date"
    set checkout_date = $user_input
    
    if $date_valid == true and $duration_valid == true
        reply "✅ 离店日期已记录：$checkout_date"
        set current_step = "select_room_type"
        reply "请选择房型（1-4）或直接告诉我房型名称"
    else
        if $date_valid == false
            reply "❌ 日期格式不正确"
        else
            reply "❌ 离店日期不能早于入住日期"
        end
    end

intent "select_room_type"
    set room_type = $user_input
    call room_info = get_room_price($room_type)
    
    if $room_info != "unknown"
        reply "✅ 已选择：$room_type"
        set current_step = "confirm_guests"
        reply "请问入住人数是多少？"
    else
        reply "❌ 房型选择无效，请重新选择"
        reply "可用房型：标准大床房、豪华双床房、行政套房、总统套房"
    end

intent "provide_guest_count"
    set guest_count = $user_input
    call max_guests = get_max_guests($room_type)
    
    if $guest_count <= $max_guests
        reply "✅ 入住人数：$guest_count 人"
        call total_price = calculate_price($room_type, $checkin_date, $checkout_date, $guest_count)
        reply "总价格：￥$total_price"
        set current_step = "confirm_booking"
        reply "请确认预订信息："
        reply "入住：$checkin_date，离店：$checkout_date"
        reply "房型：$room_type，人数：$guest_count"
        reply "总价：￥$total_price"
        reply "回复'确认'完成预订，或'取消'重新开始"
    else
        reply "❌ $room_type 最多容纳 $max_guests 人，请重新输入"
    end

intent "confirm_booking"
    if $user_input == "确认"
        call booking_ref = generate_booking_reference()
        set booking_reference = $booking_ref
        reply "🎉 预订成功！"
        reply "预订号：$booking_reference"
        reply "入住时间：下午2点后，离店时间：中午12点前"
        reply "如需修改或取消，请提供预订号"
        set current_step = "completed"
        log "完成预订：$booking_reference"
    else
        reply "预订已取消，请重新开始"
        set current_step = "welcome"
    end

intent "ask_price"
    if $room_type != "" and $checkin_date != "" and $checkout_date != ""
        call total_price = calculate_price($room_type, $checkin_date, $checkout_date, $guest_count)
        reply "💰 价格估算：￥$total_price"
    else
        reply "请先提供入住日期、离店日期和房型信息"
    end

intent "modify_booking"
    reply "请提供您的预订号"
    set current_step = "verify_booking"

intent "provide_booking_reference"
    call booking_valid = verify_booking($user_input)
    
    if $booking_valid == true
        set booking_reference = $user_input
        reply "✅ 找到预订信息"
        reply "请告诉我需要修改的内容：日期、房型或人数？"
        set current_step = "modify_details"
    else
        reply "❌ 预订号无效，请检查后重新输入"
    end

intent "cancel_booking"
    if $booking_reference != ""
        call cancel_result = cancel_booking($booking_reference)
        reply "预订已取消"
        set booking_reference = ""
        set current_step = "welcome"
    else
        reply "请先提供预订号"
    end

intent "ask_amenities"
    reply "🏊 酒店设施包括："
    reply "• 免费WiFi • 室内游泳池 • 健身中心"
    reply "• 餐厅 • 停车场 • 商务中心"
    reply "• 24小时前台服务"

intent "ask_policies"
    reply "📋 酒店政策："
    reply "• 免费取消：入住前24小时"
    reply "• 儿童政策：12岁以下免费"
    reply "• 宠物政策：不允许携带宠物"
    reply "• 吸烟政策：全酒店禁烟"

intent "help"
    reply "❓ 使用帮助："
    reply "• 查询房型：回复'房型'或'有哪些房间'"
    reply "• 开始预订：告诉我入住日期"
    reply "• 修改订单：回复'修改订单'"
    reply "• 价格查询：回复'价格'"
    reply "• 取消预订：回复'取消'"

intent "emergency"
    reply "🚨 紧急联系："
    reply "前台电话：400-123-4567"
    reply "客服邮箱：support@hotel.com"
    reply "如需紧急帮助，请直接拨打前台电话"