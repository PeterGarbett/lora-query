""" Code to return the name of the local mqtt server
Call system specific code to return name of the local broker 
default to localhost if this code does not exist """


def broker():
    """Wheres my mqtt broker ?"""
    try:
        import find_network

        broke = find_network.site()
        return broke
    except:
        return "croft"
        return "localhost"


def main():
    print(broker())


if __name__ == "__main__":
    main()
