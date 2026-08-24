import streamlit as st
import paho.mqtt.client as mqtt
import json, time, io, base64
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

st.set_page_config(page_title="IIoT Command Center", layout="wide")
st.title("🏭 IIoT Predictive Maintenance & Edge Control Center")

@st.cache_resource
def setup_mqtt_pipeline():
    buffer = []

    def on_message(client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            buffer.append(payload)
        except Exception:
            pass

    try:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    except AttributeError:
        client = mqtt.Client()

    client.on_message = on_message
    client.connect("broker.hivemq.com", 1883, 60)
    client.subscribe("iiot/factory/motor1/telemetry")
    client.loop_start()

    return client, buffer

client, buffer = setup_mqtt_pipeline()

if len(buffer) > 0:
    # Convert buffer to a shallow copy list(buffer) for thread safety
    df = pd.DataFrame(list(buffer)).tail(30)

    col1, col2, col3 = st.columns(3)
    latest_temp = df['temp'].iloc[-1]
    latest_vib = df['vib_rms'].iloc[-1]

    col1.info(f"**🌡️ Motor Temperature:** \n### {latest_temp:.1f} °C")
    col2.warning(f"**📳 Vibration RMS:** \n### {latest_vib:.2f} m/s²")

    if len(df) > 5:
        X = df.index.values.reshape(-1, 1)
        y = df['vib_rms'].values
        model = LinearRegression().fit(X, y)
        slope = model.coef_[0]
        rul = max(0, int((12.0 - latest_vib) / slope)) if slope > 0 else 999

        col3.success(f"**⏳ Estimated RUL:** \n### {rul} Secs")

        if latest_vib > 12.0:
            client.publish("iiot/factory/motor1/control", "SHUTDOWN")
            st.error("🚨 CRITICAL FAULT DETECTED: AUTO-SHUTDOWN SENT TO ESP32!")

    fig, ax1 = plt.subplots(figsize=(10, 4))
    fig.patch.set_facecolor('#0e1117')
    ax1.set_facecolor('#0e1117')

    ax1.plot(df.index, df['temp'], color='#ff4b4b', label='Temp (°C)', linewidth=2)
    ax1.set_ylabel('Temperature (°C)', color='#ff4b4b')
    ax1.tick_params(colors='white')

    ax2 = ax1.twinx()
    ax2.plot(df.index, df['vib_rms'], color='#00d4b1', label='Vibration RMS (m/s²)', linewidth=2)
    ax2.set_ylabel('Vibration RMS (m/s²)', color='#00d4b1')
    ax2.tick_params(colors='white')

    plt.title("Real-Time Machine Telemetry Stream", color='white')
    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches='tight', facecolor=fig.get_facecolor())
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig)

    st.markdown(f'<img src="data:image/png;base64,{img_str}" style="width:100%; border-radius: 8px;">', unsafe_allow_html=True)
else:
    st.info("Awaiting telemetry from Wokwi ESP32 simulation...")

time.sleep(2)
st.rerun()