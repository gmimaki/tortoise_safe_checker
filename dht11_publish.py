import os
import json
import uuid
import RPi.GPIO as GPIO
import argparse
from dataclasses import dataclass
from awscrt import mqtt, io
import time

dhtPin = 17

GPIO.setmode(GPIO.BCM)

MAX_UNCHANGE_COUNT = 100

STATE_INIT_PULL_DOWN = 1
STATE_INIT_PULL_UP = 2
STATE_DATA_FIRST_PULL_DOWN = 3
STATE_DATA_PULL_UP = 4
STATE_DATA_PULL_DOWN = 5

def read_dht11():
    GPIO.setup(dhtPin, GPIO.OUT)
    GPIO.output(dhtPin, GPIO.HIGH)
    time.sleep(0.05)
    GPIO.output(dhtPin, GPIO.LOW)
    time.sleep(0.02)
    GPIO.setup(dhtPin, GPIO.IN, GPIO.PUD_UP)

    unchanged_count = 0
    last = -1
    data = []
    while True:
        current = GPIO.input(dhtPin)
        data.append(current)
        if last != current:
            unchanged_count = 0
            last = current
        else:
            unchanged_count += 1
            if unchanged_count > MAX_UNCHANGE_COUNT:
                break

    state = STATE_INIT_PULL_DOWN

    lengths = []
    current_length = 0

    for current in data:
        current_length += 1

        if state == STATE_INIT_PULL_DOWN:
            if current == GPIO.LOW:
                state = STATE_INIT_PULL_UP
            else:
                continue
        if state == STATE_INIT_PULL_UP:
            if current == GPIO.HIGH:
                state = STATE_DATA_FIRST_PULL_DOWN
            else:
                continue
        if state == STATE_DATA_FIRST_PULL_DOWN:
            if current == GPIO.LOW:
                state = STATE_DATA_PULL_UP
            else:
                continue
        if state == STATE_DATA_PULL_UP:
            if current == GPIO.HIGH:
                current_length = 0
                state = STATE_DATA_PULL_DOWN
            else:
                continue
        if state == STATE_DATA_PULL_DOWN:
            if current == GPIO.LOW:
                lengths.append(current_length)
                state = STATE_DATA_PULL_UP
            else:
                continue
    if len(lengths) != 40:
        #print ("Data not good, skip")
        return False

    shortest_pull_up = min(lengths)
    longest_pull_up = max(lengths)
    halfway = (longest_pull_up + shortest_pull_up) / 2
    bits = []
    the_bytes = []
    byte = 0

    for length in lengths:
        bit = 0
        if length > halfway:
            bit = 1
        bits.append(bit)
    #print ("bits: %s, length: %d" % (bits, len(bits)))
    for i in range(0, len(bits)):
        byte = byte << 1
        if (bits[i]):
            byte = byte | 1
        else:
            byte = byte | 0
        if ((i + 1) % 8 == 0):
            the_bytes.append(byte)
            byte = 0
    #print (the_bytes)
    checksum = (the_bytes[0] + the_bytes[1] + the_bytes[2] + the_bytes[3]) & 0xFF
    if the_bytes[4] != checksum:
        #print ("Data not good, skip")
        return False

    return the_bytes[0], the_bytes[2]

@dataclass
class InputData:
    endpoint: str
    cert: str
    key: str
    ca: str
    topic: str

def parseArgs() -> InputData:
    parser = argparse.ArgumentParser()
    parser.add_argument('--endpoint', type=str, required=True, help="Endpoint of IoT Core")
    parser.add_argument('--cert', type=str, required=True, help="path of device certificate")
    parser.add_argument('--key', type=str, required=True, help="path of private key")
    parser.add_argument('--ca', type=str, required=True, help="path of root certificate")
    parser.add_argument('--topic', type=str, required=True, help="name of topic")

    args = parser.parse_args()

    return InputData(endpoint=args.endpoint, cert=args.cert, key=args.key, ca=args.ca, topic=args.topic)

def mqtt_connection_from_path(input: InputData) -> mqtt.Connection:
    endpoint = input.endpoint
    certPath = input.cert
    keyPath = input.key
    caPath = input.ca

    tls_ctx_options = io.TlsContextOptions.create_client_with_mtls_from_path(certPath, keyPath)
    tls_ctx_options.override_default_trust_store_from_path(None, caPath)

    port = 443 if io.is_alpn_available() else 8883

    if port == 443 and io.is_alpn_available():
        tls_ctx_options.alpn_list = ['x-amzn-mqtt-ca']

    socket_options = io.SocketOptions()
    socket_options.connect_timeout_ms = 5000
    socket_options.keep_alive = False
    socket_options.keep_alive_timeout_secs = 0
    socket_options.keep_alive_interval_secs = 0
    socket_options.keep_alive_max_probes = 0
    username = None
    client_bootstrap = io.ClientBootstrap.get_or_create_static_default()
    tls_ctx = io.ClientTlsContext(tls_ctx_options)
    mqtt_client = mqtt.Client(client_bootstrap, tls_ctx)
    proxy_options = None

    return mqtt.Connection(
        client=mqtt_client,
        on_connection_interrupted=None,
        on_connection_resumed=None,
        client_id=str(uuid.UUID(bytes=os.urandom(16), version=4)),
        host_name=endpoint,
        port=port,
        clean_session=False,
        reconnect_min_timeout_secs=5,
        reconnect_max_timeout_secs=60,
        keep_alive_secs=30,
        ping_timeout_ms=3000,
        protocol_operation_timeout_ms=0,
        will=None,
        username=username,
        password=None,
        socket_options=socket_options,
        use_websockets=False,
        websocket_handshake_transform=None,
        proxy_options=proxy_options,
        on_connection_success=None,
        on_connection_failure=None,
        on_connection_closed=None,
    )

def main(input: InputData):
    mqtt_connection = mqtt_connection_from_path(input)
    connect_future = mqtt_connection.connect()

    connect_future.result()
    print("Connected")

    message_topic = input.topic

    # Subscribe
    print("Subscribing to topic '{}'...".format(message_topic))
    subscribe_future, packet_id = mqtt_connection.subscribe(
        topic=message_topic,
        qos=mqtt.QoS.AT_LEAST_ONCE,
        callback=None)

    subscribe_result = subscribe_future.result()
    print("Subscribed with {}".format(str(subscribe_result['qos'])))

    while True:
        result = read_dht11()
        if result:
            humidity, temperature = result
            now = time.time()
            message = '{ "humidity": %s, "temperature": %s, "time": %.8f }' % (humidity, temperature, now)
            #message_json = json.dumps(message)
            #mqtt_connection.publish(topic=message_topic, payload=message_json, qos=mqtt.QoS.AT_LEAST_ONCE)
            mqtt_connection.publish(topic=message_topic, payload=message, qos=mqtt.QoS.AT_LEAST_ONCE)
        time.sleep(1)

def destroy():
    GPIO.cleanup()

if __name__ == '__main__':
    input = parseArgs()
    try:
        main(input)
    except KeyboardInterrupt:
        destroy()