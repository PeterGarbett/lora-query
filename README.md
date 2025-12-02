Query status of a remote system using lora meshtastic radios
-------------------------------------------------------------


Overview
--------

Routines for message passing between computers attached
to devices running meshtatic radios. 

In particular I use it to ask a remote system to reply with
a status string.  This is a useful back channel when internet access
fails.  The framework allows for expansion i.e. reset could be commanded.

The IP and serial interfaces to the radio were integrated.
Examples showing transmission and reception were integrated.
Then I added an interface to mqtt so I can send/receive 
using publish/subscribe on my private broker.

Numerous error conditions can arise, notably if trying to access
a radio via its IP interface when the meshtastic phone app is
also doing so. This leads to broken pipe and connection reset by peer
errors.   The policy is to detect these and exit and let systemd 
restart the program. Resynchronisation with the mqtt broker
is also dealt with this way.


Site specific items.

I wanted to make the core function available on git hub
but not share my network details. 

broker.py and response.py require some customisation, the former
to provide the ip of the local mqtt broker and the latter to
provide a routine that provides status information. broker.py
will return localhost if it doesn't know any better. My status
is formed from pinging a few devices and external addresses
and adding in the IP address . The default is just the IP address

Outline file content
--------------------

broker.py           # Provide address of the local private mqtt broker                   
command_channel.py  # The channel to use to send/listen for commands 
converse.py         # Handle the conversation 
lora.py             # Setup the interface to the meshtastic radio
query.py            # Drive radio via mqtt, keep asking until we get a response
lora-query.service  # Run the status handling as a service; restart on errors
local_mqtt.py             # Local mqtt connect, publish, subscribe
mqtt_topic.py       # Define the base topic for local mqtt
README.md           # This document
remote_status       # Fire off status request
response.py         # Definition of the commands and responses.
setup-virt          # setup python virtual environment

status.py           # Returns a site specific status string
find_network.py     # Returns location of the mqtt broker to broker.py
hosts.config	    # Site dependent lists of device names in json format
                    # mqtt server named first 



