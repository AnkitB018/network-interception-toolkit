#!/usr/bin/env python3

import scapy.all as scapy
import optparse
import subprocess
import re


def get_args():
    parser = optparse.OptionParser()

    parser.add_option("-i", "--ip", dest="ip", help="Enter the IP address or range to scan using ARP")
    
    (options, args) = parser.parse_args()

    if not options.ip:
        result = subprocess.check_output(["ifconfig", "eth0"]).decode()
        data = re.search(r"\d{3}.\d{3}\.\d\.\d{2}", result)
        if data:
            final = data.group(0) + "/24"
            return final
        else:
            print("[+] Can not read IP address to scan")
    return options.ip


def scan(ip):
    arp_request = scapy.ARP(pdst=ip)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
   

    arp_req_broadcast = broadcast/arp_request
    answered = scapy.srp(arp_req_broadcast, timeout=1, verbose=False)[0]

    client_list = []

    for element in answered:
        client_dict = {"ip": element[1].psrc, "mac": element[1].hwsrc}
        client_list.append(client_dict)

    return client_list
    
def print_result(client_list):
    print("IP \t\t\t MAC Address\n-----------------------------------------------------------")
    for element in client_list:
        print(element["ip"] + "\t\t" + element["mac"])


ip = get_args()
list = scan(ip)
print_result(list)
