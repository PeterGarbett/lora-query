""" Manage the conversation of commands and responses """

import time
import sys
import mqtt
import response

mqtt_client = None
cmd_topic = None
in_topic = None
out_topic = None

comms_error = False


def received(packet, interface, node_list, shortname, fromnum, channel, message):
    global mqtt_client
    global in_topic
    global out_topic
    global comms_error

    try:
        user = interface.getMyNodeInfo().get("user")
        ident = user.get("id")
        print("received on radio:", ident)
        in_mess = fromnum + ":" + str(channel) + ":" + message
        mqtt.publish(in_mess, in_topic, mqtt_client)
    except Exception as err:
        print(err)
        comms_error = True
        return

    # Channel 1 is encrypted so we know its authorised

    if channel == 0:
        print(f"{fromnum}:{channel}:{message}")
        return

    message.replace("\n", "")

    # Map from commands to responses

    up = response.response(message, channel)

    # Send answer back to where the query came from

    if up:
        out = fromnum + ":" + str(channel) + ":" + up + ""
        mqtt.publish(out, out_topic, mqtt_client)
        try:
            result = interface.sendText(out, destinationId=fromnum, channelIndex=1)
        except Exception as err:  # Want to catch timeout
            print("sendtext return code", result)
            print(err)
            comms_error = True


send_interface = None


def on_mqtt_message(client, userdata, msg):
    """This gets called when a command has appeared which should be in the form
    destination_id:channel:txt_message"""
    global mqtt_client
    global send_interface
    global out_topic
    global comms_error

    print(f"mqtt Received `{msg.payload.decode()}` from mqtt`{msg.topic}` topic")

    try:
        out = msg.payload.decode()
        controlStr = out.split(":")
        destId = controlStr[0]
        channel = int(controlStr[1])
        out = controlStr[2]
    except Exception as err:
        print(err, "Error parsing mqtt input", out)
        return

    try:
        mqtt.publish(out, out_topic, mqtt_client)
        print("Transmit message:", out, "destID:", destId, "channel", channel)
        send_interface.sendText(out, destinationId=destId, channelIndex=channel)
    except Exception as err:
        print(err, "Failed to send message")
        comms_error = True  # Communicate occurence of failure to the mainline


def end_loop(interface):
    """connect to mqtt, subscribe, and loop and wait - exit on error"""
    global mqtt_client
    global in_topic
    global cmd_topic
    global out_topic
    global send_interface
    global comms_error

    send_interface = interface

    try:
        user = interface.getMyNodeInfo().get("user")
        ident = user.get("id")
    except Exception as err:
        print(err)
        sys.exit()

    # Here is the ident for the radio.

    print("Using radio whose id is", ident)

    ident = ident[1:]  # remove ! from topic

    cmd_topic = "msh/EU_868/" + ident + "/" + "cmd"
    in_topic = "msh/EU_868/" + ident + "/" + "received"
    out_topic = "msh/EU_868/" + ident + "/" + "sent"

    # Setup command responses.

    response.init_responses()

    print("Start operating radio")

    try:
        mqtt_client = mqtt.connect_and_subscribe(cmd_topic, on_mqtt_message)
        mqtt_client.loop_start()
        print("mqtt interface initialised")

        # Run whenever the interface is still running
        # It drops with broken pipe etc and I can't see how to catch
        # the relevant signal or exception
        # so I just poll to see if the interface has dropped.
        # or a comms error has occurred.
        # On failure I want to exit so systemctl can restart

        active = 0
        while interface.isConnected.is_set() and not comms_error:
            sys.stdout.flush()
#
#           Let outside world know we are active

            if 0 == (active % 60):
                active = 0
                print("Alive")
            active += 1

            time.sleep(60)

        print("Interface dropped or comms error, exiting")
        mqtt_client.loop_stop()
        interface.close()
        sys.exit()

    except Exception as err:
        print("Exception in main control loop:", err)

    except KeyboardInterrupt:
        print("Script terminated by user")

    mqtt_client.loop_stop()
    interface.close()
    sys.exit()
