import paho.mqtt.client as mqtt

BROKER = "test.mosquitto.org"
PORT = 1883
TOPIC = "robot_cloud_monitor/yaseen_demo_73921/telemetry"

def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("Subscriber connected to MQTT broker!")
        client.subscribe(TOPIC)
        print(f"Listening to topic: {TOPIC}")
    else:
        print(f"Connection failed: {reason_code}")

def on_message(client, userdata, msg):
    print("\nReceived robot telemetry:")
    print(msg.payload.decode())
    print("-" * 50)

client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id="subscriber_73921"
)

client.on_connect = on_connect
client.on_message = on_message

print("Connecting to MQTT broker...")

try:
    client.connect(BROKER, PORT, 60)
    client.loop_forever()
except KeyboardInterrupt:
    print("\nSubscriber stopped.")
    client.disconnect()
except Exception as error:
    print(f"MQTT error: {error}")