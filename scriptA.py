from scapy.all import *
from scapy.layers.inet import *

# Use loopback interface
iface = "lo"
#target_ip = "127.0.0.1"
target_ip = "10.10.10.2"

# Construct L2+L3+ICMP packet
# Green Information Request Object for Interfaces (Uses Interface Identification Object, Class3 Ctype3)
hex_str = "20 00 cb ed 00 0c 03 03 00 01 04 00 0a 00 03 02"
    #       |---------| This is Header
    #0000   20 00 cb ed 00 0c 03 03 00 01 04 00 0a 00 03 02
    #                   |---------| |---------------------| This is Object H and P
    #0010   66 f4 6f 53 00 01 ad b3
rawpayload = bytes.fromhex(hex_str)
pkt = Ether(src="aa:aa:aa:aa:aa:00", dst="aa:aa:aa:aa:aa:aa")/IP(src="10.10.10.1",dst=target_ip)/ICMP(type=42, ext=ICMPExtension_Header())/Raw(load=rawpayload)
print(f"[A] Sending packet: {pkt.summary()}")

# Send packet to B
sendp(pkt, iface=iface)

# Sniff for response from B (ICMP reply)
def handle_pkt(pkt):
    if ICMP in pkt and pkt[IP].src == target_ip:
        print(f"[A] Received packet: {pkt.summary()}")
        print(f"[A] Payload: {pkt[Raw].load}")

print("[A] Waiting for response...")
sniff(iface=iface, filter="icmp", prn=handle_pkt, count=1)
