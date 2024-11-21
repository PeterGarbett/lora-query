""" Very rudimentary command/response program
At the moment I just want to issue a status string
in response to a request , and that dummied out for github
because the status is very site specific """

import public_ip

command = ["status request"]
action = []


def init_responses():
    global action
    try:

        # If software to define status isn't available

        import status

        action = [status.statstring]
    except:

        # Default to this.

        action = [public_ip.public_ip]

    return


COMMAND_CHANNEL = 1


def response(message, channel):
    global action
    if channel != COMMAND_CHANNEL:
        return ""

    message.replace("\n", "")

    try:
        index = command.index(message)
        up = action[index]()
    except:
        up = ""

    return up


def main():
    init_responses()
    rest_str = response("status request", COMMAND_CHANNEL)
    print(rest_str)


if __name__ == "__main__":
    main()
