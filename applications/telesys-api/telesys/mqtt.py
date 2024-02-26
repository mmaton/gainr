from paho.mqtt import client as paho_client
from paho.mqtt.enums import CallbackAPIVersion
from tenacity import retry, wait_random_exponential

from telesys.config import MQTT_CLIENT_ID, MQTT_BROKER, MQTT_PORT, MQTT_USERNAME, MQTT_PASSWORD, logger


def connect_mqtt():
    def on_connect(client, userdata, flags, reason_code, properties):
        print(f"Connected with result code {reason_code}")

    def on_disconnect(client, userdata, rc, *args, **kwargs):
        logger.info(f"Disconnected with result code: {rc}")

        @retry(wait=wait_random_exponential(multiplier=1, max=60), reraise=True)
        def reconnect(client):
            try:
                client.reconnect()
                logger.info("Reconnected successfully!")
                return
            except Exception as err:
                logger.error("%s. Reconnect failed. Retrying...", err)
                raise err
        reconnect(client)

    client = paho_client.Client(callback_api_version=CallbackAPIVersion.VERSION2, client_id=MQTT_CLIENT_ID)
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.connect(MQTT_BROKER, MQTT_PORT)
    return client
