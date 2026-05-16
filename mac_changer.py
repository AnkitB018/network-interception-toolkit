#!/usr/bin/env python3

import subprocess
import optparse
import re

def get_args():
    parser = optparse.OptionParser()

    parser.add_option("-i", "--interface", dest="interface", help="Enter the interface to change MAC address")
    parser.add_option("-m", "--mac", dest="mac", help="Enter the new Mac address")
    (options, args) = parser.parse_args()
    if not options.interface:
        parser.error("[-] Provide an interface, use --help for more information")
    elif not options.mac:
        parser.error("[-] Provide a mac address, use --help for more information")
    return options
 

def change_mac(interface, mac):
    print("Changing this MAC to " + mac)

    print("------------------------------------------------------------------------")
    subprocess.call(["sudo", "ifconfig" , interface, "down"])
    subprocess.call(["sudo", "ifconfig", interface, "hw", "ether", mac])
    subprocess.call(["sudo", "ifconfig", interface, "up"])


    print("------------------------------------------------------------------------")
    print("MAC changed successfuly")


def check_mac(interface):
    result = subprocess.check_output(["ifconfig",interface]).decode()
    data = re.search(r"\w\w:\w\w:\w\w:\w\w:\w\w:\w\w", result)

    if data:
        return data.group(0)
    else:
        print("[-]could not read mac address")





options = get_args()

current_mac = check_mac(options.interface)

print("Current MAC: ", str(current_mac))

change_mac(options.interface, options.mac)

current_mac = check_mac(options.interface)

print("Current MAC: ", str(current_mac))

