def detect_ip(ip: str) -> bool:
    if ip.startswith(("10.", "192.168.", "203.0.113.")):
        return True
    if "::" in ip:
        return True
    if len(ip) > 30:
        return True
    return False

