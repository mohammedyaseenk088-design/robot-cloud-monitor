import json
import sqlite3
import paho.mqtt.client as mqtt
import certifi

BROKER = "broker.hivemq.com"
PORT = 8883
TOPIC = "robot_cloud_monitor/yaseen_demo_73921/telemetry"
DATABASE = "robot_data.db"


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("Connected to MQTT broker!")
        client.subscribe(TOPIC)
        print("Waiting for telemetry...")
    else:
        print(f"Connection failed: {reason_code}")


def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())

        connection = sqlite3.connect(DATABASE)
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO telemetry (
                device_id,
                timestamp,
                acceleration_x,
                acceleration_y,
                acceleration_z,
                angular_velocity_z,
                temperature,
                humidity
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["device_id"],
            data["timestamp"],
            data["acceleration_x"],
            data["acceleration_y"],
            data["acceleration_z"],
            data["angular_velocity_z"],
            data["temperature"],
            data["humidity"]
        ))

        connection.commit()
        connection.close()

        print(
            f"Saved reading | "
            f"Temperature: {data['temperature']} °C | "
            f"Humidity: {data['humidity']}%"
        )

    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
        print(f"Invalid telemetry message: {error}")
    except sqlite3.Error as error:
        print(f"Database error: {error}")


client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id="database_subscriber_73921"
)
client.tls_set(ca_certs=certifi.where())

client.on_connect = on_connect
client.on_message = on_message

print("Starting MQTT-to-database service...")

try:
    client.connect(BROKER, PORT, 60)
    client.loop_forever()
except KeyboardInterrupt:
    print("\nDatabase subscriber stopped.")
    client.disconnect()
except Exception as error:
    print(f"MQTT error: {error}")
