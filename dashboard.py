
import json
import queue
import certifi
import pandas as pd
import plotly.express as px
import paho.mqtt.client as mqtt
import streamlit as st
from streamlit_autorefresh import st_autorefresh

BROKER = "broker.hivemq.com"
PORT = 8883

TELEMETRY_TOPIC = "robot_cloud_monitor/yaseen_demo_73921/telemetry"
COMMAND_TOPIC = "robot_cloud_monitor/yaseen_demo_73921/command"

st.set_page_config(
    page_title="Robot Cloud Monitor",
    page_icon="🤖",
    layout="wide",
)

st.title("🤖 Wheeled Robot Cloud Monitor")
st.caption("Live sensor telemetry and remote motor control")

# --------------------------------------------------
# MQTT CONNECTION
# --------------------------------------------------

@st.cache_resource
def get_mqtt_resources():
    message_queue = queue.Queue(maxsize=500)

    def on_connect(client, userdata, flags, reason_code, properties):
        if reason_code == 0:
            client.subscribe(TELEMETRY_TOPIC)

    def on_message(client, userdata, msg):
        try:
            reading = json.loads(msg.payload.decode("utf-8"))
            message_queue.put_nowait(reading)
        except (ValueError, UnicodeDecodeError, queue.Full):
            pass

    client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        client_id="cloud_dashboard_73921",
    )

    client.tls_set(ca_certs=certifi.where())
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, PORT, 60)
    client.loop_start()

    return message_queue, client


try:
    message_queue, mqtt_client = get_mqtt_resources()
except Exception as error:
    st.error(f"Could not connect to MQTT broker: {error}")
    st.stop()


# --------------------------------------------------
# ROBOT CONTROLS
# --------------------------------------------------

st.header("🎮 Robot Controls")
st.warning(
    "Test with the robot's wheels lifted off the ground first. "
    "The ESP32 firmware must support the command topic before "
    "these buttons can move the robot."
)

speed = st.slider(
    "Motor speed (%)",
    min_value=0,
    max_value=100,
    value=50,
    step=5,
)

def send_command(command):
    payload = {
        "command": command,
        "speed": speed,
    }

    result = mqtt_client.publish(
        COMMAND_TOPIC,
        json.dumps(payload),
        qos=0,
        retain=False,
    )

    if result.rc == mqtt.MQTT_ERR_SUCCESS:
        st.session_state.last_command = command
    else:
        st.error("Failed to publish command.")


if "last_command" not in st.session_state:
    st.session_state.last_command = "None"

# Directional buttons
top_left, top_center, top_right = st.columns([1, 1, 1])

with top_center:
    if st.button("⬆️ FORWARD", use_container_width=True):
        send_command("forward")

left, center, right = st.columns(3)

with left:
    if st.button("⬅️ LEFT", use_container_width=True):
        send_command("left")

with center:
    if st.button("⏹️ STOP", use_container_width=True):
        send_command("stop")

with right:
    if st.button("➡️ RIGHT", use_container_width=True):
        send_command("right")

bottom_left, bottom_center, bottom_right = st.columns([1, 1, 1])

with bottom_center:
    if st.button("⬇️ BACKWARD", use_container_width=True):
        send_command("backward")

st.info(f"Last command sent: **{st.session_state.last_command}**")

st.divider()


# --------------------------------------------------
# LIVE TELEMETRY
# --------------------------------------------------

if "readings" not in st.session_state:
    st.session_state.readings = []

while True:
    try:
        reading = message_queue.get_nowait()
    except queue.Empty:
        break

    required = [
        "timestamp",
        "temperature",
        "acceleration_x",
        "acceleration_y",
        "acceleration_z",
        "angular_velocity_z",
    ]

    if all(key in reading for key in required):
        st.session_state.readings.append(reading)

st.session_state.readings = st.session_state.readings[-200:]

st_autorefresh(interval=2000, key="mqtt_refresh")

if not st.session_state.readings:
    st.info(
        "Waiting for sensor readings. Start the MQTT publisher "
        "or connect the ESP32 telemetry firmware."
    )
    st.stop()

df = pd.DataFrame(st.session_state.readings)

df["timestamp"] = pd.to_datetime(
    df["timestamp"],
    utc=True,
    errors="coerce",
)

df = df.dropna(subset=["timestamp"]).sort_values("timestamp")

if df.empty:
    st.warning("Waiting for valid timestamp readings.")
    st.stop()

latest = df.iloc[-1]

c1, c2, c3, c4 = st.columns(4)

c1.metric("Temperature", f"{latest['temperature']:.2f} °C")

if "humidity" in df.columns and pd.notna(latest.get("humidity")):
    c2.metric("Humidity", f"{latest['humidity']:.2f} %")
else:
    c2.metric("Humidity", "Not available")

c3.metric("Acceleration X", f"{latest['acceleration_x']:.3f} m/s²")
c4.metric(
    "Angular Velocity Z",
    f"{latest['angular_velocity_z']:.3f} rad/s",
)

st.divider()
st.subheader("Acceleration Over Time")

acceleration_df = df[
    ["timestamp", "acceleration_x", "acceleration_y", "acceleration_z"]
].melt(
    id_vars="timestamp",
    var_name="Axis",
    value_name="Acceleration (m/s²)",
)

fig_acc = px.line(
    acceleration_df,
    x="timestamp",
    y="Acceleration (m/s²)",
    color="Axis",
)

st.plotly_chart(fig_acc, width="stretch")

left, right = st.columns(2)

with left:
    fig_temp = px.line(
        df,
        x="timestamp",
        y="temperature",
        title="Temperature Over Time",
        labels={"temperature": "Temperature (°C)"},
    )
    st.plotly_chart(fig_temp, width="stretch")

with right:
    if "humidity" in df.columns:
        fig_humidity = px.line(
            df,
            x="timestamp",
            y="humidity",
            title="Humidity Over Time",
            labels={"humidity": "Humidity (%)"},
        )
        st.plotly_chart(fig_humidity, width="stretch")

st.subheader("Recent Telemetry Records")

st.dataframe(
    df.tail(20).sort_values("timestamp", ascending=False),
    width="stretch",
)

