
![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![ESP32](https://img.shields.io/badge/ESP32-C%2B%2B-green?logo=expressif)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red?logo=streamlit)
![MQTT](https://img.shields.io/badge/MQTT-HiveMQ-orange?logo=hivemq)

# 🏭 IIoT-Based Predictive Maintenance & Closed-Loop Control System

An enterprise-grade Industrial Internet of Things (IIoT) edge-to-cloud platform. This project simulates real-time machine telemetry, extracts high-frequency vibration metrics on an ESP32 edge node, estimates Remaining Useful Life (RUL) using machine learning in the cloud, and executes closed-loop safety shutdowns to prevent catastrophic equipment failures.

---

## 📁 Repository Structure
```

.
├── wokwi/                      # Edge Firmware & Hardware Simulation
│   ├── diagram.json            # Wokwi circuit layout configuration
│   └── sketch.ino              # C++ Firmware for ESP32 edge device
│
├── python/                     # Cloud Analytics & UI Dashboard
│   ├── IIoT_Pipeline.ipynb     # Google Colab notebook workflow
│   ├── app.py                  # Streamlit control dashboard & ML engine
│   └── requirements.txt        # Python dependency definitions
│
└── README.md                   # System documentation

```

---

## 📌 Key System Features

* **Edge Digital Signal Processing (DSP):** Computes Vibration Root Mean Square (RMS) directly on the ESP32 to isolate mechanical bearing noise.
* **Interactive Hardware Simulation:** Features physical-type controls in Wokwi (DHT22 temperature sensor, slide potentiometer for wear dynamics, and dual status LEDs).
* **Predictive ML Analytics:** Uses time-series linear regression models to continuously calculate Remaining Useful Life (RUL) in seconds.
* **Closed-Loop Safety Actuation:** Sends automated MQTT control payloads back to the ESP32 when vibration crosses critical safety thresholds ($> 12.0 \text{ m/s}^2$), triggering hardware relay cutoffs.
* **Real-Time Operations Center:** Visualizes multi-sensor trends dynamically via in-memory Base64 rendering to avoid network bundle drops.

---

## 🏗 System Architecture


```

┌───────────────────────────┐                ┌─────────────────────────┐
│     Wokwi ESP32 Edge      │ --(Telemetry)->│      HiveMQ Broker      │
│  - DHT22 (Temperature)   │   JSON Topic   │ (broker.hivemq.com:1883)│
│  - Potentiometer (Wear)   │                └────────────┬────────────┘
│  - Edge DSP Vibration RMS │                             │
│  - Status LEDs (Run/Trip) │<--(Shutdown)─               │
└───────────────────────────┘   Control Topic             │
▼
┌─────────────────────────┐
│   Streamlit Dashboard   │
│  - Real-time Plotting   │
│  - Linear Regression RUL│
│  - Automated Trip Logic │
└─────────────────────────┘

```

---

## 🛠 Tech Stack

| Domain | Technologies Used |
| :--- | :--- |
| **Edge Hardware / Firmware** | ESP32, C++, FreeRTOS/Arduino Framework, PubSubClient, Adafruit DHT |
| **Messaging Protocol** | MQTT over WebSockets / TCP (HiveMQ Public Broker) |
| **Cloud Dashboard & Analytics** | Python 3.10+, Streamlit, Pandas, Matplotlib, Scikit-Learn |
| **Simulation Environment** | Wokwi Embedded Simulator, Google Colab, Localtunnel |

---

## 📐 Mathematical Model & Algorithms

### 1. Vibration RMS Calculation (Edge)
The ESP32 samples high-frequency analog signals from the potentiometer, overlays sinusoidal motor oscillations, and computes the Root Mean Square (RMS):

$$\text{RMS} = \sqrt{\frac{1}{N} \sum_{i=1}^{N} x_i^2}$$

### 2. Remaining Useful Life (RUL) Estimation (Cloud)
The cloud engine fits an ordinary least squares (OLS) linear regression line on the sliding window of vibration history to predict when the machine will reach its critical threshold ($V_{\text{critical}} = 12.0 \text{ m/s}^2$):

$$y = \beta_1 X + \beta_0 \implies \text{RUL} = \max\left(0, \left\lfloor\frac{12.0 - y_{\text{current}}}{\beta_1}\right\rfloor\right)$$

---

## 🚀 Quickstart Guide

### Step 1: Launch the Virtual Edge Device (`/wokwi`)
1. Open the [Wokwi ESP32 Simulator](https://wokwi.com).
2. Copy `wokwi/diagram.json` into the layout editor.
3. Install `DHT sensor library` and `PubSubClient` via the Wokwi Library Manager.
4. Paste `wokwi/sketch.ino` into the main code tab and press **Play**.

### Step 2: Run Cloud Analytics Dashboard (`/python`)
1. Open `python/IIoT_Pipeline.ipynb` in Google Colab.
2. Run the environment setup cells to install dependencies and generate `app.py`.
3. Launch Streamlit and Localtunnel:
   ```bash
   !streamlit run app.py & npx -y localtunnel --port 8501
4. Copy the IP address printed by `!curl ipv4.icanhazip.com`, open the generated `.loca.lt` link, and paste the IP into the Endpoint authentication box.

```

```
