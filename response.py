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
    """Setup commands and corresponding responses. Much of this is site
    specific so provide a placeholder if not available"""

    global action
    global command

    try:

        # If software to define status is available

        import status

        action = [status.statstring, reset.reset]
        command = ["status", "reset"]
    except:

        # Default to this.

        command = ["status request"]
        action = [public_ip.public_ip]

    return


def response(fromnum, channel, message):
    """Look up command and action it"""
    global action
    global command

    debug = True

    if channel != COMMAND_CHANNEL:
        return (False, "")

    message.replace("\n", "")

    if debug:
        print("Interpret:", message)

    """ message is assummed to be in two parts, separate out and pass on the 2nd as an argument """

    try:
        decomposed = message.split(" ")
        index = command.index(decomposed[0])
        if len(decomposed) == 1:
            up = action[index]("")
        else:
            up = action[index](decomposed[-1])

    except Exception as err:
        if debug:
            print(err)
        return (False, "")

    if debug:
        print("response:", up)

    return (True, up)


def main():
    init_responses()
    rest_str = "status request"
    response("FAFC", COMMAND_CHANNEL, rest_str)
    rest_str = "reset edge"
    response("FAFC", COMMAND_CHANNEL, rest_str)
    rest_str = "reset"
    response("FAFC", COMMAND_CHANNEL, rest_str)


if __name__ == "__main__":
    main()
