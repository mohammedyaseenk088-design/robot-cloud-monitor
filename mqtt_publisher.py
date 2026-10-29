import json
import random
import time
from datetime import datetime, timezone
import paho.mqtt.client as mqtt
import certifi
BROKER = "broker.hivemq.com"

PORT = 8883
TOPIC = "robot_cloud_monitor/yaseen_demo_73921/telemetry"


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("Publisher connected to MQTT broker!")
    else:
        print(f"Connection failed: {reason_code}")


client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id="robot_simulator_73921"
)
client.tls_set(ca_certs=certifi.where())

client.on_connect = on_connect

print("Connecting to MQTT broker...")
client.connect(BROKER, PORT, 60)
client.loop_start()

try:
    time.sleep(2)

    while True:
        reading = {
            "device_id": "robot_01",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "acceleration_x": round(random.uniform(-1.5, 1.5), 3),
            "acceleration_y": round(random.uniform(-1.5, 1.5), 3),
            "acceleration_z": round(random.uniform(8.0, 11.0), 3),
            "angular_velocity_z": round(random.uniform(-0.5, 0.5), 3),
            "temperature": round(random.uniform(25, 35), 2),
            "humidity": round(random.uniform(40, 80), 2)
        }

        result = client.publish(TOPIC, json.dumps(reading))
        result.wait_for_publish()

        print("Published:", json.dumps(reading))
        time.sleep(2)

except KeyboardInterrupt:
    print("\nPublisher stopped.")

finally:
    client.loop_stop()
    client.disconnect()
    
