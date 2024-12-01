""" Very rudimentary command/response program
At the moment I just want to issue a status string
in response to a request , and that dummied out for github
because the status is very site specific """

import public_ip
import reset

action = []


def init_responses():
    global action
    global command

    try:

        # If software to define status is available

        import status

        action = [status.statstring,reset.reset]
        command = ["status request","reset"]
    except:

        # Default to this.

        command = ["status request"]
        action = [public_ip.public_ip]

    return


COMMAND_CHANNEL = 1


def response(fromnum,channel,message):
    global action
    global command 

    debug = False

    if channel != COMMAND_CHANNEL:
        return (False,"")

    message.replace("\n", "")

    if debug:
        print("Interpret:",message)

    try:
        index = command.index(message)
        up = action[index]()
    except Exception as err:
        if debug:
            print(err)
        return (False,"")

    out = fromnum + ":" + str(channel) + ":" + up 

    return (True,out)


def main():
    init_responses()
    rest_str = response("DEAD", COMMAND_CHANNEL,"status request")
    print(rest_str)
    rest_str = response("FAFC", COMMAND_CHANNEL,"reset")
    print(rest_str)


if __name__ == "__main__":
    main()
