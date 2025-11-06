from scapy.all import *
from scapy.layers.inet import *

iface = "lo"
listen_ip = "10.10.10.2"

# Set flag: 1 = modify payload, 0 = pure ICMP reply
probeflag = 1
greenflag = 1

def handle_pkt(pkt):
    if IP in pkt and ICMP in pkt and (pkt[ICMP].type == 8 or pkt[ICMP].type == 42) and pkt[IP].dst == listen_ip:
        # Ignore packets sent by ourselves
        if pkt[IP].src == listen_ip:
            return

        # Get payload if it exists
        payload = pkt[Raw].load #payload = pkt[Raw].load if Raw in pkt else b""
        print(f"[B] Received ICMP: {payload}")

        # Decide payload based on flags
        if (greenflag == 1 and probeflag == 1):
            extended_echo_reply_header = "2b 00 62 50 00 00 00 06"
            extension_header = "2000dcf4"
            node_power_object = "000C090100000064000000504b76f46600000000dfbc0900000000001c1d1e1f202122232425262728292a2b2c2d2e2f3031323334353637"
            new_payload = payload.hex()+node_power_object
            #       |---------| This is Header
            #0000   20 00 dc f4 00 0C 09 01 00 00 00 64 00 00 00 50
            #                   |---------| |---------------------| This is Object H and P
            #0010   4b 76 f4 66 00 00 00 00 df bc 09 00 00 00 00 00 
            #0020   1c 1d 1e 1f 20 21 22 23 24 25 26 27 28 29 2a 2b 
            #0030   2c 2d 2e 2f 30 31 32 33 34 35 36 37
            rawpayload = bytes.fromhex(new_payload)
        elif (greenflag == 1):
            extended_echo_reply_header = "2b 00 62 50 00 00 00 e0"
            extension_header = "2000dcf4"
            node_power_object = "000C090100000064000000504b76f46600000000dfbc0900000000001c1d1e1f202122232425262728292a2b2c2d2e2f3031323334353637"
            new_payload = extension_header + node_power_object
            rawpayload = bytes.fromhex(new_payload)
        else:
            extended_echo_reply_header = "2b 00 62 50 00 00 00 06"
            new_payload = ""  # pure ICMP reply
            rawpayload = payload
        
        # Build ICMP Extended Echo Reply #1
        
        # 0000   2b 00 62 56 00 00 00 06 20 00 cb ed 00 0c 03 03
        # 0010   00 01 04 00 0a 00 03 02 00 0c 09 01 00 00 00 64
        # 0020   00 00 00 50 4b 76 f4 66 00 00 00 00 df bc 09 00
        # 0030   00 00 00 00 1c 1d 1e 1f 20 21 22 23 24 25 26 27
        # 0040   28 29 2a 2b 2c 2d 2e 2f 30 31 32 33 34 35 36 37
        reply = Ether(src=pkt[Ether].dst, dst=pkt[Ether].src)/ \
                IP(src=pkt[IP].dst, dst=pkt[IP].src, proto=1)/ \
                Raw(load=bytes.fromhex(extended_echo_reply_header)+rawpayload)

        sendp(reply, iface=iface)
        if probeflag == 1:
            print("[B] Sent ICMP Echo Reply with modified payload")
        else:
            print("[B] Sent pure ICMP Echo Reply")

print("[B] Waiting for ICMP Echo Requests...")
sniff(iface=iface, filter="icmp", prn=handle_pkt)
