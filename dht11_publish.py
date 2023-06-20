import RPi.GPIO as GPIO
import argparse
from dataclasses import dataclass
from awscrt import mqtt, http, io
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

def parseArgs() -> InputData:
    parser = argparse.ArgumentParser()
    parser.add_argument('--endpoint', type=str, required=True, help="Endpoint of IoT Core")
    parser.add_argument('--cert', type=str, required=True, help="path of device certificate")
    parser.add_argument('--key', type=str, required=True, help="path of private key")
    parser.add_argument('--ca', type=str, required=True, help="path of root certificate")

    args = parser.parse_args()

    return InputData(endpoint=args.endpoint, cert=args.cert, key=args.key, ca=args.ca)

def mqtt_connection_from_path(input: InputData) -> mqtt.Connection:
    certPath = input.cert
    keyPath = input.key
    caPath = input.ca

    tls_ctx_options = io.TlsContextOptions.create_client_with_mtls_from_path(certPath, keyPath)
    tls_ctx_options.override_default_trust_store_from_path(None, caPath)

    port = 443 if io.is_alpn_available() else 8883
    # ここまでやった

    if port == 443 and io.is_alpn_available() and use_custom_authorizer is False:
        tls_ctx_options.alpn_list = ['http/1.1'] if use_websockets else ['x-amzn-mqtt-ca']

    socket_options = io.SocketOptions()
    socket_options.connect_timeout_ms = _get(kwargs, 'tcp_connect_timeout_ms', 5000)
    # These have been inconsistent between keepalive/keep_alive. Resolve both for now to ease transition.
    socket_options.keep_alive = \
        _get(kwargs, 'tcp_keep_alive', _get(kwargs, 'tcp_keepalive', False))

    socket_options.keep_alive_timeout_secs = \
        _get(kwargs, 'tcp_keep_alive_timeout_secs', _get(kwargs, 'tcp_keepalive_timeout_secs', 0))

    socket_options.keep_alive_interval_secs = \
        _get(kwargs, 'tcp_keep_alive_interval_secs', _get(kwargs, 'tcp_keepalive_interval_secs', 0))

    socket_options.keep_alive_max_probes = \
        _get(kwargs, 'tcp_keep_alive_max_probes', _get(kwargs, 'tcp_keepalive_max_probes', 0))

    username = _get(kwargs, 'username', '')
    if _get(kwargs, 'enable_metrics_collection', True):
        username += _get_metrics_str(username)

    if username == "":
        username = None

    client_bootstrap = _get(kwargs, 'client_bootstrap')
    if client_bootstrap is None:
        client_bootstrap = io.ClientBootstrap.get_or_create_static_default()

    tls_ctx = io.ClientTlsContext(tls_ctx_options)
    mqtt_client = awscrt.mqtt.Client(client_bootstrap, tls_ctx)

    proxy_options = kwargs.get('http_proxy_options', kwargs.get('websocket_proxy_options', None))
    return mqtt.Connection(
        client=mqtt_client,
        on_connection_interrupted=_get(kwargs, 'on_connection_interrupted'),
        on_connection_resumed=_get(kwargs, 'on_connection_resumed'),
        client_id=_get(kwargs, 'client_id'),
        host_name=_get(kwargs, 'endpoint'),
        port=port,
        clean_session=_get(kwargs, 'clean_session', False),
        reconnect_min_timeout_secs=_get(kwargs, 'reconnect_min_timeout_secs', 5),
        reconnect_max_timeout_secs=_get(kwargs, 'reconnect_max_timeout_secs', 60),
        keep_alive_secs=_get(kwargs, 'keep_alive_secs', 1200),
        ping_timeout_ms=_get(kwargs, 'ping_timeout_ms', 3000),
        protocol_operation_timeout_ms=_get(kwargs, 'protocol_operation_timeout_ms', 0),
        will=_get(kwargs, 'will'),
        username=username,
        password=_get(kwargs, 'password'),
        socket_options=socket_options,
        use_websockets=use_websockets,
        websocket_handshake_transform=websocket_handshake_transform,
        proxy_options=proxy_options,
        on_connection_success=_get(kwargs, 'on_connection_success'),
        on_connection_failure=_get(kwargs, 'on_connection_failure'),
        on_connection_closed=_get(kwargs, 'on_connection_closed'),
    )


def main(input: InputData):
    while True:
        result = read_dht11()
        if result:
            humidity, temperature = result
            # TODO ここでpublish
            print ("humidity: %s %%,  Temperature: %s C`" % (humidity, temperature))
        time.sleep(1)

def destroy():
    GPIO.cleanup()

if __name__ == '__main__':
    input = parseArgs()
    try:
        main(input)
    except KeyboardInterrupt:
        destroy()