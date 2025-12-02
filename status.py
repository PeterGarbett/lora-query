#!/usr/bin/python3
""" Check a few ip addresses to assess the status of the system """

import os
import sys
import find_network
import public_ip
import broker



def status(test_hostname):

    debug = False

    try:
        response = os.system("ping -c 1 -w2 " + test_hostname + " > /dev/null 2>&1")

        if response != 0:
            if debug:
                print(test_hostname, "ignoring pings")
            return False

    except Exception as err:
        if debug:
            print(err)
        return False

    return True


def statstring(arg):

    targets = [
        "0.0.0.0",
        "google.com",
    ]

    targets += find_network.site_members()

    up = ""
    for target in targets:
        found = status(target)
        if found:
            up += "1"
        else:
            up += "0"

    ip = public_ip.public_ip()

    mqtt = broker.broker()

    return mqtt + " " + up + " " + ip


def parse_statstring(status):

    debug = False

    if debug:
        print("string to parse:", status)

    #   Leading with this or not... don't care either way

    if status[0] == ">":
        status = status[1:]

    try:
        decomp = status.split(" ")
        remote_broker = decomp[0]
        status_bits = decomp[1]
        ip_address = decomp[2]
    except Exception as err:
        print(err)
        return

    targets = [
        "nameserver",
        "Internet",
    ]

    targets += find_network.local_nodes(remote_broker)

    if debug:
        print(
            "broker:",
            remote_broker,
            "status bits:",
            status_bits,
            "IP address",
            ip_address,
        )
        print("Nodes", targets)

    if len(targets) != len(status_bits):
        return (remote_broker, ip_address, [])

    live = []
    for index in enumerate(targets):
        live.append((status_bits[index[0]], index[1]))

    return (remote_broker, ip_address, live)


def pretty_print(status):

    try:
        print("IP   :", status[1])
        print("mqtt :", status[0], " ")
        live = status[2]

        for ping_target in live:
            if ping_target[0] == "1":
                print("up   :", ping_target[1])
            else:
                print("down :", ping_target[1])

    except Exception as err:
        print(err)
        return




def main():

    none_null = bool(len(sys.argv) - 1)

    up = statstring("dummy")

    # Default to pretty printing, suppress if any arguments supplied

    if none_null:
        print(up)
    else:
        parsed = parse_statstring(up)
        pretty_print(parsed)


if __name__ == "__main__":
    main()
