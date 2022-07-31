"""
Some example code to test our serial port and IoT connection.
Reads lines of text from the serial port and sends them to
the AWS IoT MQTT topic, receives from the same topic and
then prints the message information. 
"""
import json
import os
import time
import serial
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from dotenv import load_dotenv

load_dotenv()


def custom_callback(client, userdata, message):
    # pylint: disable=unused-argument
    """Handles MQTT message received callbacks.

    Args:
        client (Any): Publishing client.
        userdata (Any): Userdata?
        message (Any): The received message.
    """
    print("Received a new message: ")
    print(message.payload)
    print("from topic: ")
    print(message.topic)
    print("--------------\n\n")


def main():
    """Main entrypoint function."""
    com_port = os.environ.get("SERIAL_COM_PORT")
    print(f"Using serial COM port: {com_port}")

    baud_rate = os.environ.get("SERIAL_BAUD_RATE")
    print(f"Using serial baud rate: {baud_rate}")

    client_id = os.environ.get("AWS_IOT_CLIENT_ID")
    print(f"Using AWS IoT client ID: {client_id}")

    host = os.environ.get("AWS_IOT_ENDPOINT")
    print(f"Using AWS IoT endpoint: {host}")

    port = int(os.environ.get("AWS_IOT_PORT"))
    print(f"Using AWS IoT port: {port}")

    root_ca_path = os.environ.get("AWS_IOT_ROOT_CA_PATH")
    print(f"Using AWS IoT root CA path: {root_ca_path}")

    private_key_path = os.environ.get("AWS_IOT_PRIVATE_KEY_PATH")
    print(f"Using AWS IoT private key path: {private_key_path}")

    certificate_path = os.environ.get("AWS_IOT_CERTIFICATE_PATH")
    print(f"Using AWS IoT certificate path: {certificate_path}")

    topic = os.environ.get("AWS_IOT_TEST_TOPIC")
    print(f"Using AWS IoT test topic: {topic}")

    # Init AWSIoTMQTTClient
    mqtt_client = AWSIoTMQTTClient(client_id)
    mqtt_client.configureEndpoint(host, port)
    mqtt_client.configureCredentials(root_ca_path, private_key_path, certificate_path)

    # AWSIoTMQTTClient connection configuration
    mqtt_client.configureAutoReconnectBackoffTime(1, 32, 20)
    mqtt_client.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
    mqtt_client.configureDrainingFrequency(2)  # Draining: 2 Hz
    mqtt_client.configureConnectDisconnectTimeout(10)  # 10 sec
    mqtt_client.configureMQTTOperationTimeout(5)  # 5 sec

    # Connect and subscribe to AWS IoT
    mqtt_client.connect()
    mqtt_client.subscribe(topic, 1, custom_callback)
    time.sleep(2)

    with serial.Serial(com_port, baud_rate) as ser:
        if not ser.is_open:
            ser.open()
        loop_count = 0
        while True:
            received = ser.readline()
            publish_message = {}
            publish_message["message"] = received.decode()
            publish_message["sequence"] = loop_count
            message_json = json.dumps(publish_message)
            mqtt_client.publish(topic, message_json, 1)
            loop_count += 1


if __name__ == "__main__":
    main()
