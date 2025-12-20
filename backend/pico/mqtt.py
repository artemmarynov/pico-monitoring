from umqtt.simple import MQTTClient

def connect_mqtt(client_id: str, broker: str, port: int = 1883, keepalive: int = 60) -> MQTTClient:
    client = MQTTClient(
        client_id=client_id,
        server=broker,
        port=port,
        keepalive=keepalive,
    )
    client.connect()
    print("✓ MQTT connected")
    return client
