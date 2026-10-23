import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px
from streamlit_autorefresh import st_autorefresh

DATABASE = "robot_data.db"

st.set_page_config(
    page_title="Robot Cloud Monitor",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Wheeled Robot Monitoring Dashboard")
st.caption("Real-time IoT telemetry monitoring")
st_autorefresh(interval=2000, key="robot_refresh")



@st.cache_data(ttl=1)
def load_data():
    connection = sqlite3.connect(DATABASE)
    try:
        df = pd.read_sql_query(
            "SELECT * FROM telemetry ORDER BY id ASC",
            connection
        )
    finally:
        connection.close()

    if not df.empty:
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)

    return df


df = load_data()

if df.empty:
    st.warning("No telemetry data found. Start the MQTT publisher and database subscriber.")
    st.stop()

latest = df.iloc[-1]

# Latest readings
col1, col2, col3, col4 = st.columns(4)

col1.metric("Temperature", f"{latest['temperature']:.2f} °C")
col2.metric("Humidity", f"{latest['humidity']:.2f} %")
col3.metric("Acceleration X", f"{latest['acceleration_x']:.3f} m/s²")
col4.metric("Angular velocity Z", f"{latest['angular_velocity_z']:.3f} rad/s")

st.divider()

# Acceleration chart
st.subheader("Acceleration Over Time")

acceleration_df = df[
    ["timestamp", "acceleration_x", "acceleration_y", "acceleration_z"]
].melt(
    id_vars="timestamp",
    var_name="Axis",
    value_name="Acceleration (m/s²)"
)

fig_acc = px.line(
    acceleration_df,
    x="timestamp",
    y="Acceleration (m/s²)",
    color="Axis",
    title="Accelerometer Readings"
)

st.plotly_chart(fig_acc, use_container_width=True)

# Temperature and humidity charts
col5, col6 = st.columns(2)

with col5:
    st.subheader("Temperature")
    fig_temp = px.line(
        df,
        x="timestamp",
        y="temperature",
        title="Temperature Over Time",
        labels={"temperature": "Temperature (°C)"}
    )
    st.plotly_chart(fig_temp, use_container_width=True)

with col6:
    st.subheader("Humidity")
    fig_humidity = px.line(
        df,
        x="timestamp",
        y="humidity",
        title="Humidity Over Time",
        labels={"humidity": "Humidity (%)"}
    )
    st.plotly_chart(fig_humidity, use_container_width=True)

st.subheader("Recent Telemetry Records")
st.dataframe(df.tail(20).sort_values("id", ascending=False), use_container_width=True)

st.caption(f"Total readings stored: {len(df)}")
