Query status of a remote system using lora
------------------------------------------

Routines for message passing between computers attached
to devices running meshtatic. 

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
restart the program.

broker.py and response.py require some customisation, the former
to provide the ip of the local mqtt broker and the latter to
provide a routine that provides status information. broker.py
will return localhost if it doesn't know any better. My status
is formed from pinging a few devices and external addresses
and adding in the IP address . The default is just the IP address



broker.py       # Provide address of the local private mqtt broker                   
converse.py     # Handle the conversation 
lora.py         # Setup the interface to the meshtastic radio
query.py        # Drive radio via mqqt, keep asking until we get a response
lora.service    # Run the status handling as a service; restart on errors
mqtt.py         # Local mqtt connect, publish, subscribe
README.md       # This document
response.py     # Definition of the commands and responses.
setup-virt      # setup python virtual environment

status.py       - not present. Returns a site specific status string
find_network.py - not present. Returns location of the mqtt broker




