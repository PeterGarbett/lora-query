""" Very rudimentary command/response program
At the moment I just want to issue a status string
in response to a request , and that dummied out for github
because the status is very site specific """

import public_ip
import small_timestamps
import command_channel

COMMAND_CHANNEL = command_channel.COMMAND_CHANNEL


action = []


def ip(dummy):
    """Responses get called with an argument we need to ditch"""
    return public_ip.public_ip()


def init_responses():
    """Setup commands and corresponding responses. Much of this is site
    specific so provide a placeholder if not available"""

    global action
    global command

    try:

        # If software to define status and perform reset is available

        import status
        import reset

        command = ["status", "reset"]
        action = [status.statstring, reset.reset]
    except:

        # Default to this.

        command = ["status"]
        action = [ip]

    return


def response(fromnum, channel, message):
    """Look up command and action it"""
    global action
    global command

    debug = False

    if channel != COMMAND_CHANNEL or len(message) == 0:
        return (False, "")

    message.replace("\n", "")

    if debug:
        print("Interpret:", message)

    # Is this message marked as a response ? ignore it

    if message[0] == ">":
        print("Message is a response to us, no reply needed")
        return (False, "")

    """ message is assummed to be in two parts, separate out and pass on the 2nd as an argument """

    try:
        decomposed = message.split(" ")

        # Commands and node names must not match.  A reply triggers a silent exception

        index = command.index(decomposed[0])
        if len(decomposed) == 1:
            up = action[index]("")
        else:
            up = action[index](decomposed[-1])

        # Precede responses with a > to distinguish them from requests

        up = ">" + up  #   identify as a response

    except Exception as err:
        if debug:
            print(err)
        return (False, "")

    if debug:
        print("response:", up)

    return (True, up)


def main():
    ''' crude test program '''
    init_responses()
    rest_str = "status request"
    response("FAFC", COMMAND_CHANNEL, rest_str)
    rest_str = "reset edge"
    response("FAFC", COMMAND_CHANNEL, rest_str)
    rest_str = "reset"
    response("FAFC", COMMAND_CHANNEL, rest_str)


if __name__ == "__main__":
    main()
