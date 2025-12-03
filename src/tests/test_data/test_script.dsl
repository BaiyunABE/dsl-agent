step "greeting"
    reply "你好！欢迎使用我们的服务。"
    log "用户进入问候步骤"

step "help"
    reply "我可以帮您解答以下问题：1. 产品咨询 2. 技术支持 3. 投诉建议"
    wait "product" "support" "complaint"

step "thanks"
    reply "不用客气！有什么其他问题吗？"

step "farewell"
    reply "感谢使用，再见！"