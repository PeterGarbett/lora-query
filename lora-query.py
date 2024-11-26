import time
import sys
from pubsub import pub
from meshtastic.tcp_interface import TCPInterface
from meshtastic.serial_interface import SerialInterface
from meshtastic import portnums_pb2
import converse

node_ip = "127.0.0.1"
serial_port = "/dev/ttyACM0"  # Initial guess


def get_node_infoTCP(node_ip):
    print("Initializing TcpInterface to get node info...")
    try:
        local = TCPInterface(hostname=node_ip)
        node_info = local.nodes
        local.close()
        print("Node info retrieved.")
        return node_info
    except Exception as err:
        print(err)
        sys.exit()


def get_node_info_serial(serial_port):
    print("Initializing SerialInterface to get node info...")
    try:
        local = SerialInterface(serial_port)
        node_info = local.nodes
        local.close()
        print("Node info retrieved.")
        return node_info
    except Exception as err:
        print(err)
        sys.exit()


def parse_node_info(node_info):
    print("Parsing node info...")
    nodes = []
    for node_id, node in node_info.items():
        nodes.append(
            {
                "num": node_id,
                "user": {"shortName": node.get("user", {}).get("shortName", "Unknown")},
            }
        )
    print("Node info parsed.")
    return nodes


def parse_packet(packet, interface, node_list):

    packet_type = None
    
    try:
        packet_type = packet["decoded"].get("portnum")

    except Exception as err:
        print("Error decoding packet", err)
        return  

    if packet_type != "TEXT_MESSAGE_APP":
        return

    try:
        message = packet["decoded"]["payload"].decode("utf-8")
    except Exception as err:
        print("Message extraction:", err)
        message = "error:undecoded"

    try:
        fromnum = packet["fromId"]
    except Exception as err:
        print("Finding source radio:", err)
        fromnum = "Unknown"

    try:
        channel = packet["channel"]
    except Exception as err:
        print("Error in channel determination:", err)
        channel = -1

    try:
        shortname = next(
            (node["user"]["shortName"] for node in node_list if node["num"] == fromnum),
            "Unknown",
        )

    except Exception as err:
        print("lora-query exception:", err)
    # except KeyError:
    #    pass  # Ignore KeyError silently
    except UnicodeDecodeError:
        pass  # Ignore UnicodeDecodeError silently

    converse.received(
        packet, interface, node_list, shortname, fromnum, channel, message
    )


def on_receive(packet, interface, node_list):
    parse_packet(packet, interface, node_list)


use_serial = False


def main():
    global use_serial
    global serial_port
    inputargs = sys.argv
    sys.argv.pop(0)
    use_serial = False

    if len(inputargs) == 0:
        use_serial = True
        print("Using serial interface", serial_port)
    else:
        if len(inputargs) != 1:
            print("usage: python3 read_messages_tcp.py node")
            sys.exit()
        else:
            node_ip = inputargs[0]
            print(f"Using node IP: {node_ip}")

    # Retrieve and parse node information
    # I'm assumming only one serial device, on /dev/ttyUSB0 or /dev/ttyACM0
    # Which works for my current use case

    try:
        if use_serial:
            try:
                node_info = get_node_info_serial(serial_port)
            except:
                print(serial_port, "not found")
                serial_port = "/dev/ttyUSB0"
                node_info = get_node_info_serial(serial_port)
        else:
            node_info = get_node_infoTCP(node_ip)

        node_list = parse_node_info(node_info)
    except Exception as err:
        print(err)
        if use_serial:
            print("serial port:", serial_port, " not found")
        else:
            print("node:", node_ip, " not found")
        sys.exit()

    # Print node list for debugging
    print("Node List:")
    for node in node_list:
        print(node)

    # Subscribe the callback function to message reception
    def on_receive_wrapper(packet, interface):
        on_receive(packet, interface, node_list)

    try:
        pub.subscribe(on_receive_wrapper, "meshtastic.receive")
    except Exception as err:
        print("Failed to subscribe to meshtastic.receive", err)
        sys.exit()

    print("Subscribed to meshtastic.receive")

    # Set up the Interface for message listening

    try:
        if use_serial:
            interface = SerialInterface(serial_port)
        else:
            interface = TCPInterface(hostname=node_ip)
    except:
        print("Failed to setup interface.")
        sys.exit()

    print("Radio Interface setup")

    # Keep the script running to listen for messages

    converse.end_loop(interface)


if __name__ == "__main__":
    main()
