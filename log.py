def append_log(log_text, message):
    """로그 창에 메시지 추가"""
    log_text.append(message)  # 메시지 추가
    log_text.ensureCursorVisible()  # 자동 스크롤
