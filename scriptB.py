from scapy.all import *

iface = "lo"
listen_ip = "10.10.10.2"

def handle_pkt(pkt):
    if ICMP in pkt and pkt[ICMP].type == 8 and pkt[IP].dst == listen_ip:
        print(f"[B] Received packet: {pkt.summary()}")
        print(f"[B] Original Payload: {pkt[Raw].load}")

        # Modify payload
        new_payload = pkt[Raw].load + b" + modified by B"

        # Build ICMP Echo Reply
        reply = Ether(src=pkt[Ether].dst, dst=pkt[Ether].src)/ \
                IP(src=pkt[IP].dst, dst=pkt[IP].src)/ \
                ICMP(type=0, id=pkt[ICMP].id, seq=pkt[ICMP].seq)/ \
                Raw(load=new_payload)

        sendp(reply, iface=iface)
        print(f"[B] Sent ICMP Echo Reply with modified payload")

print("[B] Waiting for ICMP Echo Requests...")
sniff(iface=iface, filter="icmp", prn=handle_pkt)
