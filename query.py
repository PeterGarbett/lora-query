""" Send status queries from a system with a local radio to a remote
system with a radio, using mqtt as an interface.  Lora is inherently unreliable so try repeatedly
until we get an answer. A few tries is enough in my case - 2 miles, urban environment  """

import time
import sys
from multiprocessing import Queue
import queue
import paho.mqtt.client as mqtt
import broker
import mqtt
import random

local_radio_id = None
remote_radio_id = None
topic = None
message = None
channel = 1
broker = broker.broker()

QUEUE_CHECK_INTERVAL = 1  # Period in seconds to check for incoming messages
RESEND_RATE = (
    60  # Resend request at this number of check intervals (greater than lora limit)
)

mqttc = None

message_input = Queue()


def on_mqtt_message(client, userdata, message):
    """This gets called back by mqtt, put the message on a queue
    to get it to the mainline code"""
    global message_input
    #    print("mqtt message:", (message.payload).decode())
    message_input.put((message.payload).decode())


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
    """Form a command"""
    base_message = "!" + radio + ":" + str(channel) + ":"
    command = base_message + message

    return command


def query():
    """Send off a status query at intervals until a reply appears"""
    global message_input
    global mqttc
    global message
    global topic
    global local_radio_id
    global remote_radio_id

    inputargs = sys.argv
    sys.argv.pop(0)

    if len(inputargs) != 2:
        print(usage)
        sys.exit()
    else:
        local_radio_id = str(inputargs[0])
        remote_radio_id = str(inputargs[1])

        valid_radio_id("local", local_radio_id)
        valid_radio_id("remote", remote_radio_id)

    print(f"Using local radio: {local_radio_id} remote radio: {remote_radio_id}")

    command = form_command(remote_radio_id, channel, "status request")

    topic = "msh/EU_868/" + local_radio_id + "/"
    cmd_topic = topic + "cmd"
    in_topic = topic + "received"

    client_id = "ID-" + local_radio_id + "-" + str(random.randint(0, 1000))
    print("mqtt client ID:", client_id)

    mqttc = mqtt.connect_and_subscribe("ID" + local_radio_id, in_topic, on_mqtt_message)

    mqttc.loop_start()
    once = False

    prod = 0

    try:
        while True:

            if 0 == prod % RESEND_RATE:
                mqtt.publish(command, cmd_topic, mqttc)
            prod += 1

            sys.stdout.flush()

            try:
                input_message = message_input.get_nowait()
                if local_radio_id in input_message and remote_radio_id in input_message:
                    print("Received>", input_message, "<")
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
