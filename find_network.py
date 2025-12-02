""" Return the list of names on the current natwork, and 
the mqtt server which is the first name on the list """

import subprocess
import json


def load_config(config):
    """Load possible device names list from a json file"""
    try:
        with open(config, "r", encoding="ascii") as f:
            hosts = json.load(f)
            return hosts

    except Exception as err:
        print(err)
        return []

    return []


def local_nodes(node):
    """Return list of nodes given one ... beware there are duplicates"""

# Fixed location for now .. to be improved

    hosts = load_config("/home/embed/lora-query/hosts.config")

    for nodelist in enumerate(hosts):
        elements = nodelist[1]

        if node in elements:
            return elements

    return []


def site():
    """Returns the site name which is the first on the list and is our mqtt server"""
    response = subprocess.check_output("hostname", shell=True, text=True)
    response = response.replace("\n", "")
    response = response.lower()

    nodelist = local_nodes(response)
    if response in nodelist:
        return nodelist[0]

    return []


def site_members():
    """Return the list of names of devices on this network"""
    response = subprocess.check_output("hostname", shell=True, text=True)
    response = response.replace("\n", "")
    response = response.lower()

    return local_nodes(response)


if __name__ == "__main__":
    print("Our mqtt server is here :", site())
    print("We are a member of", site_members())
