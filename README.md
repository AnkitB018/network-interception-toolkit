# network-mitm-toolkit

A Python-based toolkit for packet interception, ARP spoofing, DNS spoofing, traffic analysis, and MITM-related networking experiments using Scapy and NetfilterQueue.

⚠️ This project is currently under development.

---

# 1. Requirements

- Python 3
- Linux based system (tested on Kali Linux)
- Root privileges for most scripts
- Scapy
- NetfilterQueue

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# 2. Usage

All scripts can be launched using the main toolkit entrypoint:

```bash
python3 main.py <command> [options]
```

Available commands:

```bash
change-mac
net-scan
arp-spoof
dns-spoof
sniff
```

Toolkit help:

```bash
python3 main.py -h
```

Version:

```bash
python3 main.py --version
```

Script-specific help:

```bash
python3 main.py sniff -h
```

---

# 3. MAC Changer

Changes the MAC address of a selected network interface.

Useful for:
- MAC randomization
- Identity masking in local networks
- Testing MAC-based filtering

Command:

```bash
python3 main.py change-mac -i <interface> -m <new_mac>
```

Example:

```bash
python3 main.py change-mac -i eth0 -m 00:11:22:33:44:55
```

Options:

```text
-i, --interface    Interface to modify
-m, --mac          New MAC address
```

Notes:
- Requires root privileges
- Interface may temporarily disconnect during MAC change

---

# 4. Network Scanner

Scans a target IP or subnet using ARP requests and identifies active hosts.

Useful for:
- Discovering devices on local network
- Reconnaissance
- Internal network mapping

Command:

```bash
python3 main.py net-scan -i <target_ip_or_range>
```

Example:

```bash
python3 main.py net-scan -i 192.168.1.0/24
```

Options:

```text
-i, --ip    Target IP or subnet
```

Notes:
- Works only on local network
- Uses ARP scanning
- Fast and reliable for LAN discovery

---

# 5. ARP Spoofer

Performs ARP spoofing / ARP poisoning between a target and gateway.

Useful for:
- Man-in-the-middle (MITM) attacks
- Packet interception
- DNS spoofing setups
- Traffic analysis

Command:

```bash
python3 main.py arp-spoof -t <target_ip> -g <gateway_ip>
```

Example:

```bash
python3 main.py arp-spoof -t 192.168.1.5 -g 192.168.1.1
```

Options:

```text
-t, --target     Target machine IP
-g, --gateway    Gateway/router IP
```

Important:
- IP forwarding must be enabled
- FORWARD policy may need to be ACCEPT
- Works only on IPv4
- IPv6 traffic is not affected by ARP spoofing

Enable forwarding:

```bash
echo 1 | sudo tee /proc/sys/net/ipv4/ip_forward
sudo iptables --policy FORWARD ACCEPT
```

Notes:
- Automatically restores ARP tables on exit
- Required for remote DNS spoofing and packet interception

---

# 6. DNS Spoofer

Intercepts and modifies DNS responses using NetfilterQueue.

Useful for:
- DNS spoofing
- Redirecting victim traffic
- Local phishing simulations
- DNS interception experiments

Command:

```bash
python3 main.py dns-spoof -u <victim_domain> -t <spoof_ip>
```

Example:

```bash
python3 main.py dns-spoof -u example.com -t 192.168.1.10
```

Local testing:

```bash
python3 main.py dns-spoof --local-test
```

Net cut mode:

```bash
python3 main.py dns-spoof -c
```

Options:

```text
-u, --url          Target domain to spoof
-t, --target       IP to redirect victim toward
--local-test       Uses INPUT/OUTPUT queues instead of FORWARD
-c, --cut          Drops all packets in queue
```

Important:
- Remote spoofing requires ARP spoofing first
- Requires IP forwarding
- Requires FORWARD policy ACCEPT
- Works only for unencrypted DNS traffic
- HTTPS websites will still show certificate warnings even if DNS spoof succeeds
- Modern systems using DoH/DoT/DNSCrypt may bypass spoofing entirely

Notes:
- Net cut mode can be used to verify MITM forwarding path
- IPv6 traffic is not spoofed
- Local test mode is useful for debugging

---

# 7. Packet Sniffer

Captures and analyzes network packets using Scapy.

Supports:
- HTTP request sniffing
- POST data extraction
- DNS packet monitoring

Command:

```bash
python3 main.py sniff -i <interface>
```

DNS-only mode:

```bash
python3 main.py sniff -i <interface> -d
```

Example:

```bash
python3 main.py sniff -i eth0
```

Options:

```text
-i, --interface    Interface to sniff
-d, --dns          DNS sniffing mode
```

Features:
- Extracts visited HTTP URLs
- Detects possible POST credentials
- DNS mode shows:
  - A records
  - AAAA records
  - MX records
  - CNAME records
  - resolved IPs

Important:
- HTTP traffic is visible directly
- HTTPS traffic is encrypted and request contents are not visible
- DNS records for HTTPS websites may still be visible in DNS mode
- DNSCrypt / DoH / DoT may hide DNS traffic from normal sniffing

Notes:
- DNS mode is useful for monitoring domain resolutions
- Credential extraction works only on unencrypted HTTP traffic

---

# 8. Project Status

Current features:
- MAC changer
- Network scanner
- ARP spoofing
- DNS spoofing
- Packet sniffing
- NetfilterQueue experimentation

Planned future additions:
- HTTPS bypass experiments
- File interception
- Code injection
- Better CLI packaging
- Global install support
- Improved logging and formatting

---

# 9. Disclaimer

This project is created strictly for:
- educational purposes
- cybersecurity learning
- local lab experimentation
- authorized testing environments

Do not use these tools against systems or networks without proper authorization.
