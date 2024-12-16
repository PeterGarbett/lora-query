""" Manage the conversation of commands and responses """

import time
import sys
import threading
import response
import random
import small_timestamps
import local_mqtt
import mqtt_topic


mqtt_client = None
cmd_topic = None
in_topic = None
out_topic = None

CMD_CHANNEL = 1

comms_error = False


def add_timestamp(message):
    """Add leading timestamp"""

    timestamp_appended = str(small_timestamps.small_timestamp_mins()) + ":" + message

    return timestamp_appended


def remove_timestamps(times_and_message):

    decomposed = times_and_message.split(":")

    return decomposed[-1]


def received_from_lora(
    packet, interface, node_list, shortname, fromnum, channel, message
):
    global mqtt_client
    global in_topic
    global out_topic
    global comms_error

    debug = False

    try:
        user = interface.getMyNodeInfo().get("user")
        ident = user.get("id")
        print("received on radio:", ident)

        channel_str = str(channel)
        in_mess = fromnum + ":" + channel_str + ":" + add_timestamp(message)
        if not local_mqtt.publish(in_mess, in_topic, mqtt_client):
            comms_error = True

    except Exception as err:
        print("converse.received error", err)
        comms_error = True
        return

    # The command channel is encrypted so we know its authorised
    # Filter out the others
    if channel != CMD_CHANNEL:
        print(f"{fromnum}:{channel}:{message}")
        try:
            import send_email

            send_email.message(
                "lora radio " + ident + " received message",
                fromnum + ":" + channel_str + ":" + message,
            )
        except Exception as err:
            print("Error calling message.message", err)
        return

    message.replace("\n", "")

    # Map from commands to responses

    try:
        deco = message.split(":")
        timestamp = float(deco[0])
        now = small_timestamps.small_timestamp_mins()
        delay = small_timestamps.time_difference_in_minutes(timestamp, now)
        print("Message started off ", delay, " minutes ago")

        if 20.0 < delay:
            print("Reject stale message")
            return

    except Exception as err:
        print("Missing timestamp:", err, "in message:", message)

    noTime = remove_timestamps(message)
    out = response.response(fromnum, channel, noTime)

    # Send answer back to where the query came from
    # Wrap it up in timestamp format ....

    if out[0]:
        try:
            resp = add_timestamp(out[1])
            # reply = fromnum + ":" + str(CMD_CHANNEL) + ":" + resp
            reply = add_timestamp(fromnum + ":" + str(CMD_CHANNEL) + ":" + out[1])
            print("Transmit resp=", reply)

            result = interface.sendText(
                reply, destinationId=fromnum, channelIndex=channel
            )
            if not local_mqtt.publish(resp, out_topic, mqtt_client):
                comms_error = True

            if debug:
                print("sendtext return code", result)
        except Exception as err:  # Want to catch timeout
            print(err)
            comms_error = True


def decompose_mqtt_message(target):
    """Decompose message delimited by ":"'s into a tuple"""
    decomp = target.split(":")

    debug = False

    if debug:
        print("Decompose message of length", len(decomp))

    if len(decomp) < 3:
        return None

    radio = decomp[0]
    channel = decomp[1]

    if debug:
        print("Radio:", radio, "Channel:", channel)

    #   This fiddly bit is so no-one gets a surprise when
    #   including a ":" in a message

    payloadList = decomp[2:]

    payload = payloadList[0]
    for x in payloadList[1:]:
        payload += ":"
        payload += x

    return (radio, channel, payload)


send_interface = None


def on_mqtt_message(client, userdata, msg):
    """This gets called when a command has appeared which should be in the form
    destination_id:channel:txt_message.  It then sends out the message with those
    parameters and publishes it"""
    global mqtt_client
    global send_interface
    global out_topic
    global comms_error

    print(f"mqtt Received `{msg.payload.decode()}` from mqtt`{msg.topic}` topic")

    try:
        out = msg.payload.decode()
        deco = decompose_mqtt_message(out)
        if None == deco:
            print(err, "Error parsing mqtt input", out)
            return
        destId = deco[0]
        channel = int(deco[1])
        out = deco[2]
    except Exception as err:
        print(err, "Error parsing mqtt input", out)
        return

    try:
        print("Transmit message:", out, "destID:", destId, "channel", channel)
        send_interface.sendText(out, destinationId=destId, channelIndex=channel)

        if not local_mqtt.publish(out, out_topic, mqtt_client):
            comms_error = True  # Communicate occurence of failure to the mainline

    except Exception as err:
        print(err, "Failed to send message")
        comms_error = True  # Communicate occurence of failure to the mainline


def crash(args):
    global comms_error

    print("Exception caught in crash handler")
    print(
        f"caught {args.exc_type} with value {args.exc_value} in thread {args.thread}\n"
    )
    comms_error = True


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

    BASE = mqtt_topic.BASE
    cmd_topic = BASE + ident + "/" + mqtt_topic.CMD
    in_topic = BASE + ident + "/" + mqtt_topic.REC
    out_topic = BASE + ident + "/" + mqtt_topic.SENT

    # Setup command responses.

    response.init_responses()

    print("Start operating radio")

    threading.excepthook = crash

    try:
        # Subscribe so we can receive commands to respond to by sending messages

        client_id = "ID-" + ident + "-" + str(random.randint(0, 1000))
        print("mqtt client id:", client_id)

        mqtt_client = local_mqtt.connect_and_subscribe(
            client_id, cmd_topic, on_mqtt_message
        )

        # Treat failure of mqtt broker as fatal so we attempt reconnect via systemd

        if mqtt_client == None:
            interface.close()
            sys.exit()

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
                alive = threading.active_count()
                print("Alive with ", alive, " active threads:")
            active += 1
            time.sleep(60)

        print("Interface dropped or comms error, exiting")

    except Exception as err:
        print("Exception in main control loop:", err)

    except KeyboardInterrupt:
        print("Script terminated by user")

    mqtt_client.loop_stop()
    interface.close()
    sys.exit()
