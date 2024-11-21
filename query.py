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


local_radio_id = None
remote_radio_id = None
topic = None
message = None
channel = 1
broker = broker.broker()


mqttc = None


message_input = Queue()


def on_mqtt_message(client, userdata, message):
    """This gets called back by mqtt, put the message on a queue
    to get it to the mainline code"""
    global message_input
    print("mqtt message:", (message.payload).decode())
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


def query():
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

    message = "!" + remote_radio_id + ":" + str(channel) + ":status request"

    topic = "msh/EU_868/" + local_radio_id + "/"
    cmd_topic = topic + "cmd"
    in_topic = topic + "received"

    mqttc = mqtt.connect_and_subscribe(in_topic, on_mqtt_message)

    try:
        mqttc.loop_start()

        message_rec = False
        while not message_rec:
            mqtt.publish(message, cmd_topic, mqttc)
            time.sleep(60)  # Sleep to give time for message to be picked up
            sys.stdout.flush()
            try:
                while True:
                    message = message_input.get_nowait()
                    if local_radio_id in message and remote_radio_id in str(message):
                        print("remote system status :>", message, "<")
                        mqttc.loop_stop()
                        message_rec = True
                        break
            except queue.Empty:
                time.sleep(45)
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
