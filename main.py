import argparse
import subprocess
import sys

commands = {
    "change-mac": "scripts/mac_change.py",
    "net-scan": "scripts/net_scanner.py",
    "arp-spoof": "scripts/arp_spoof.py",
    "dns-spoof": "scripts/dns_spoof.py",
    "sniff": "scripts/packet_sniffer.py"
}

# Forward script-specific help directly
if len(sys.argv) >= 3 and sys.argv[2] in ["-h", "--help"]:
    command = sys.argv[1]

    if command in commands:
        subprocess.call(
            ["python3", commands[command], sys.argv[2]]
        )
        sys.exit(0)

parser = argparse.ArgumentParser()

subparsers = parser.add_subparsers(dest="command")

for cmd in commands:
    subparsers.add_parser(cmd)

args, remaining = parser.parse_known_args()

if args.command in commands:
    subprocess.call(
        ["python3", commands[args.command]] + remaining
    )

else:
    parser.print_help()
