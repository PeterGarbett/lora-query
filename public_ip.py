#!/usr/bin/python3
#
#
#
import requests
import json
import os
from requests import get


def public_ip():
    """Find and return our public IP if possible"""
    debug = False
    # Find out what IP we currently have

    if debug:
        print("Retrieving external IP address")
    try:
        ip = get("https://api.ipify.org").content.decode("utf8")
    except:
        if debug:
            print("Failed to get IP address")
        ip = "None"

    return ip


def main():
    """Test entry point"""
    print(public_ip())


if __name__ == "__main__":
    main()
