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
        index = command.index(message)
        up = action[index]()
    except Exception as err:
        if debug:
            print(err)
        return (False, "")

    if debug:
        print("response:", up)

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
