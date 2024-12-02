""" Very rudimentary command/response program
At the moment I just want to issue a status string
in response to a request , and that dummied out for github
because the status is very site specific """

import public_ip
import reset
import small_timestamps

COMMAND_CHANNEL = 1

action = []


def init_responses():
    global action
    global command

    try:

        # If software to define status is available

        import status

        action = [status.statstring, reset.reset]
        command = ["status request", "reset"]
    except:

        # Default to this.

        command = ["status request"]
        action = [public_ip.public_ip]

    return


def form_command(radio, channel, message):
    """Form a command including a timestamp"""
    base_message = (
        radio
        + ":"
        + str(channel)
        + ":"
        + str(small_timestamps.small_timestamp_mins())
        + ":"
    )
    command = base_message + message

    return command


def response(fromnum, channel, message):
    global action
    global command

    debug = False

    if channel != COMMAND_CHANNEL:
        return (False, "")

    message.replace("\n", "")

    if debug:
        print("Interpret:", message)

    try:
        deco = message.split(":")
        timestamp = float(deco[0])
        message = deco[1]
    except Exception as err:
        print("Missing timestamp:", err)
        return (False, "")

    now = small_timestamps.small_timestamp_mins()
    delay = small_timestamps.time_difference_in_minutes(timestamp, now)

    print("Message started off ", delay, " minutes ago")

    if 20.0 < delay:
        print("Reject stale message")
        return (False,"")


    try:
        index = command.index(message)
        up = action[index]()
    except Exception as err:
        if debug:
            print(err)
        return (False, "")

    if debug:
        print("response:",up)

    return (True, up)


def main():
    init_responses()
    now = small_timestamps.small_timestamp_mins()
    rest_str = response("DEAD", COMMAND_CHANNEL, str(now) + ":status request")
    print(rest_str)


#    rest_str = response("FAFC", COMMAND_CHANNEL,"reset")
#    print(rest_str)


if __name__ == "__main__":
    main()
