from scapy.all import *
import time

# ========== 用户配置 ==========
TARGET_IP = "2406:2d40:7383:5700::1"   # 目标 IPv6 地址
TARGET_PORT = 54321                    # UDP 端口
PAYLOAD = b"test"                      # 数据包内容
TIMEOUT = 3.0                          # 最长等待时间（秒）
# ==============================

def measure_udp_ipv6_rtt(dst_ip, dst_port, payload, timeout=3.0):
    # 构造 UDP over IPv6 数据包
    pkt = IPv6(dst=dst_ip)/UDP(dport=dst_port, sport=RandShort())/Raw(load=payload)

    # 记录发送时间
    send_time = time.time()

    # 发送并嗅探回应（使用 L2 层发送以避免内核干扰）
    ans = sr1(pkt, timeout=timeout, verbose=0)

    # 记录接收时间
    recv_time = time.time()

    if ans is None:
        print(f"[✗] No reply from {dst_ip}:{dst_port} (timeout after {timeout}s)")
        return None
    elif ans.haslayer(ICMPv6DestUnreach):
        rtt = (recv_time - send_time) * 1000  # 转换为毫秒
        print(f"[✓] Reply from {dst_ip}: RTT = {rtt:.2f} ms (ICMPv6 Destination Unreachable)")
        return rtt
    else:
        print(f"[?] Unexpected reply from {dst_ip}: {ans.summary()}")
        return None

# 运行一次测量
if __name__ == "__main__":
    measure_udp_ipv6_rtt(TARGET_IP, TARGET_PORT, PAYLOAD, timeout=TIMEOUT)
