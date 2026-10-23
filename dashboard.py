import json
import queue
import threading

import pandas as pd
import plotly.express as px
import paho.mqtt.client as mqtt
import streamlit as st
from streamlit_autorefresh import st_autorefresh

BROKER = "test.mosquitto.org"
PORT = 1883
TOPIC = "robot_cloud_monitor/yaseen_demo_73921/telemetry"

st.set_page_config(
    page_title="Robot Cloud Monitor",
    page_icon="🤖",
    layout="wide",
)

st.title("🤖 Wheeled Robot Monitoring Dashboard")
st.caption("Live telemetry received through MQTT")

# A thread-safe queue stores incoming MQTT messages.
@st.cache_resource
def get_mqtt_resources():
    message_queue = queue.Queue(maxsize=500)

    def on_connect(client, userdata, flags, reason_code, properties):
        if reason_code == 0:
            client.subscribe(TOPIC)

    def on_message(client, userdata, msg):
        try:
            reading = json.loads(msg.payload.decode("utf-8"))
            message_queue.put_nowait(reading)
        except (ValueError, UnicodeDecodeError, queue.Full):
            pass

    client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2,
        client_id="cloud_dashboard_73921",
    )
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

if "readings" not in st.session_state:
    st.session_state.readings = []

# Move messages from the MQTT thread into Streamlit's session.
while True:
    try:
        reading = message_queue.get_nowait()
    except queue.Empty:
        break

    required = [
        "timestamp",
        "temperature",
        "humidity",
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
        "Waiting for MQTT readings. Start mqtt_publisher.py "
        "on your laptop and wait a few seconds."
    )
    st.stop()

df = pd.DataFrame(st.session_state.readings)
df["timestamp"] = pd.to_datetime(
    df["timestamp"], utc=True, errors="coerce"
)
df = df.dropna(subset=["timestamp"]).sort_values("timestamp")

if df.empty:
    st.warning("Waiting for valid timestamp readings.")
    st.stop()

latest = df.iloc[-1]

c1, c2, c3, c4 = st.columns(4)
c1.metric("Temperature", f"{latest['temperature']:.2f} °C")
c2.metric("Humidity", f"{latest['humidity']:.2f} %")
c3.metric("Acceleration X", f"{latest['acceleration_x']:.3f} m/s²")
c4.metric("Angular Velocity Z", f"{latest['angular_velocity_z']:.3f} rad/s")

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
