""" Send status queries from a system with a local radio to a remote
system with a radio, using mqtt as an interface.  Lora is inherently unreliable so try repeatedly
until we get an answer. A few tries is enough in my case - 2 miles, urban environment  """

import time
import sys
from multiprocessing import Queue
import queue
import paho.mqtt.client as mqtt
import broker
import random
import small_timestamps
import mqtt_topic
import local_mqtt
import mqtt_topic

local_radio_id = None
remote_radio_id = None
topic = None
message = None
channel = 1
broker = broker.broker()

QUEUE_CHECK_INTERVAL = 1  # Period in seconds to check for incoming messages
ATTEMPT_LIMIT = 10  # Request status this many times before giving up
RESEND_RATE = (
    60  # Resend request at this number of check intervals (greater than lora limit)
)
LOCAL_RADIO_CHECK = 2

radio_is_alive = False
mqttc = None

message_input = Queue()


def on_mqtt_message(client, userdata, message):
    """This gets called back by mqtt, put the message on a queue
    to get it to the mainline code"""
    global message_input

    debug = False

    if debug:
        print("mqtt message:", (message.payload).decode())

    topic = message.topic

    if mqtt_topic.SENT in topic:
        if debug:
            print("mqtt says radio xmit")
        radio_is_alive = True
        return

    if mqtt_topic.CMD in topic:
        if debug:
            print("mqtt command sent")
        return

    if mqtt_topic.REC in topic:
        try:
            payload = (message.payload).decode()
            message_input.put(payload)
        except Exception as err:
            print(err)  # decoding error probably

        # Ignore anything not in these catagories


usage = "usage: python3 lora_remote_status_request.py local_radio_id remote_radio_id"


def valid_radio_id(dest, digits):
    """This is user input from the command line so can easily be in error
    We will at least check its 8 hex digits"""

    err_mess = "Invalid " + dest + " radio id"

    if 8 != len(digits):
        print(err_mess, digits)
        sys.exit()

    try:
        value = int(digits, 16)
    except:
        print(err_mess, digits)
        sys.exit()


def form_command(radio, channel, message):
    """Form a command including a timestamp"""

    debug = False

    base_message = (
        radio
        + ":"
        + str(channel)
        + ":"
        + str(small_timestamps.small_timestamp_mins())
        + ":"
    )
    command = base_message + message

    if debug:
        print("form message from", base_message, " combined with ", message)

    return command


def query():
    """Default: Send off command at intervals until a reply appears
    default to a status enquiry, can be overidden by a command line parameter"""
    global message_input
    global mqttc
    global message
    global topic
    global local_radio_id
    global remote_radio_id
    global radio_is_alive

    debug = False

    inputargs = sys.argv
    sys.argv.pop(0)

    if len(inputargs) < 2:
        print(usage)
        sys.exit()
    local_radio_id = str(inputargs[0])
    remote_radio_id = str(inputargs[1])

    valid_radio_id("local", local_radio_id)
    valid_radio_id("remote", remote_radio_id)

    # Default to "status request" , can overide from command line

    if 3 <= len(inputargs):
        cli_command = inputargs[2]
    else:
        cli_command = "status request"

    print(f"Using local radio: {local_radio_id} remote radio: {remote_radio_id}")

    command = form_command("!" + remote_radio_id, channel, cli_command)

    if debug:
        print("Command is:", command)

    topic = mqtt_topic.BASE + local_radio_id + "/"
    cmd_topic = topic + mqtt_topic.CMD
    radio_activity_topic = topic + "#"

    client_id = "ID-" + local_radio_id + "-" + str(random.randint(0, 1000))

    if debug:
        print("mqtt client ID:", client_id)

    try:
        mqttc = local_mqtt.connect_and_subscribe(
            client_id, radio_activity_topic, on_mqtt_message
        )
    except Exception as err:
        print(err)
        sys.exit()

    mqttc.loop_start()

    prod = 0
    attempts = 0

    try:
        while True:

            if 0 == prod % RESEND_RATE:
                # Command the radio via mqtt. Hope it is listening
                local_mqtt.publish(command, cmd_topic, mqttc)
                if radio_is_alive:
                    print(".", end="")
                else:
                    print("*", end="")

                attempts += 1

                if ATTEMPT_LIMIT <= attempts:
                    print("\nNo luck, giving up")
                    break
            prod += 1

            sys.stdout.flush()

            try:
                input_message = message_input.get_nowait()
                if local_radio_id in input_message and remote_radio_id in input_message:

                    if cli_command != "status request":
                        print("Received:", input_message)
                        break

                    if debug:
                        print("Received:", input_message)
                    input_message = input_message[2:]
                    decomp = input_message.split(":")
                    print("\n")
                    try:
                        import status

                        output = status.parse_statstring(decomp[-1])
                        status.pretty_print(output)
                    except Exception as err:
                        if debug:
                            print(err)
                        print("Remote status:", decomp[-1])

                    break

                time.sleep(QUEUE_CHECK_INTERVAL)
                continue

            except queue.Empty:
                time.sleep(1)
                continue
            except Exception as err:
                print(err)

    except Exception as err:
        print(err)
    except KeyboardInterrupt:
        print("Script terminated by user")

    mqttc.loop_stop()


if __name__ == "__main__":
    query()
