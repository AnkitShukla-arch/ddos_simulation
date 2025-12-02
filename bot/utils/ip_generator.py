import random
import ipaddress
from .traffic_modes import MALICIOUS_WEIGHTS

def ipv4_random():
    return ".".join(str(random.randint(0,255)) for _ in range(4))

def ipv6_random():
    return str(ipaddress.IPv6Address(random.getrandbits(128)))

def ipv4_mal():
    return random.choice([
        f"10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}",
        f"192.168.{random.randint(0,10)}.{random.randint(0,255)}",
        ".".join(str(i) for i in random.sample(range(256), 4)),
    ])

def ipv6_mal():
    return f"2001:db8::{random.randint(0,9999)}:{random.randint(0,9999)}"

def generate_ip(mode, ipv4_ratio):
    mal_prob = MALICIOUS_WEIGHTS[mode]
    is_mal = random.random() < mal_prob

    ipv4 = random.random() < ipv4_ratio

    if is_mal:
        ip = ipv4_mal() if ipv4 else ipv6_mal()
    else:
        ip = ipv4_random() if ipv4 else ipv6_random()

    return ip, is_mal

