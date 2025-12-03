step "start"
    reply "欢迎！请输入您的姓名："
    wait "name_input"

step "name_input"
    reply "您好，" + $user_input + "！请问需要什么帮助？"
    log "用户姓名：" + $user_input
    wait "help" "info"

step "help"
    reply "帮助内容：..."
    wait "more_help" "back"

step "info"
    reply "公司信息：..."
    wait "contact" "back"