""" mqtt connect, subscribe and publish routines for paho mqtt V2 """

import sys
import random
from paho.mqtt import client as mqtt_client
import broker

# Generate a Client ID with the subscribe prefix.
client_id = f"subscribe-{random.randint(0, 100)}"

# This is correct for my broker

anonymous = True
username = ""
password = ""
port = 1883
debug = False


def subscribe(topic, on_message, client: mqtt_client):
    """Subscribe to mqtt"""
    print("subscribe to ", topic)
    try:
        client.subscribe(topic)
        client.on_message = on_message
    except Exception as err:
        print("Failed to subscribe to ", topic)
        print(err)
        sys.exit()


def connect_and_subscribe(topic, message_handler) -> mqtt_client:
    """Version 2 paho mqtt connect and subscribe routine"""

    def on_connect(client, userdata, flags, reason_code, properties):
        if reason_code.is_failure:
            print(
                f"Failed to connect: {reason_code}. loop_forever() will retry connection"
            )

    try:
        client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION2, client_id)

        if not anonymous:
            client.username_pw_set(username, password)

        client.on_connect = on_connect
        mqtt_broker = broker.broker()
        print("Attempt to use broker", mqtt_broker)
        client.connect(mqtt_broker, port)
        subscribe(topic, message_handler, client)
        return client

    except Exception as err:
        print(err)
        sys.exit()


def publish(msg, topic, client):
    """Publish message on topic using client"""
    if debug:
        print("mqtt publish:", msg, "to", topic)
    result = client.publish(topic, msg)
    # result: [0, 1]
    status = result[0]
    if status == 0:
        print(f"Sent `{msg}` to mqtt topic `{topic}`")
    else:
        print(f"Failed to send mqtt message to topic {topic}", status)


def main():
    """Test routine"""

    def on_message(client, userdata, msg):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")

    topic = "stat/tasmota_8CA606/RESULT"
    client = connect_and_subscribe(topic, on_message)
    ptopic = "msh/EU_868/"
    publish("hello::", ptopic, client)
    client.loop_forever()


if __name__ == "__main__":
    """Call test routine if called directly"""
    main()
