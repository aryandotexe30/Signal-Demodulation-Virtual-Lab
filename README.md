# 🌾 AgroSphere — Digital Twin on Smart Farming using IoT & ML

> A real-time Digital Twin platform for smart agriculture that monitors crop health, predicts yield, and automates irrigation using IoT sensors and in-browser Machine Learning.

---

## 🚀 Live Demo

Open `AgroSphere.html` directly in any modern browser — no server or installation required.

---

## 📌 About the Project

AgroSphere creates a **Digital Twin** of a physical paddy (rice) farm by mirroring real-world sensor data into a synchronized 3D virtual model. It combines IoT hardware, cloud connectivity, and ML inference to give farmers real-time insights and automated control over their crops.

The entire frontend — including the 3D render, ML model, charts, and IoT pipeline visualization — is packaged into a **single self-contained HTML file**.

---

## ✨ Features

- **3D Digital Twin** — Interactive Three.js render of the crop field, synchronized with live sensor data
- **Real-Time Sensor Monitoring** — Tracks soil moisture, temperature, humidity, and sensor battery
- **ML Inference (In-Browser)** — TensorFlow.js model that classifies crop health, forecasts yield (kg/hectare), and recommends irrigation
- **Automated Irrigation Control** — Toggle between Manual and Auto mode; pump relay triggered by ML output
- **Live Weather Integration** — Pulls real-time weather data for SRMIST Kattankulathur via Open-Meteo API
- **Sensor Time Series Charts** — Chart.js powered graphs for all sensor readings
- **IoT Pipeline Visualization** — Visual flow from physical sensors → Arduino → MQTT → ML → Dashboard
- **Event Log** — Real-time alert log with severity levels (info, warning, critical, ok)
- **CSV Export** — Download sensor history as a CSV file
- **Voice Alerts** — Browser speech synthesis for critical notifications
- **System Architecture Diagram** — SVG diagram of the full hardware-software stack
- **Crop Detail Panel** — Click the 3D crop to see full metrics, ML advisory, and growth stage

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| 3D Visualization | Three.js r128 + OrbitControls |
| ML / AI | TensorFlow.js 4.10 |
| Charts | Chart.js |
| Weather API | Open-Meteo (Kattankulathur, TN) |
| IoT Hardware | Arduino Uno + ESP8266 Wi-Fi Module |
| Sensors | Capacitive Soil Moisture, DHT11, LDR, INA219 |
| Connectivity | MQTT (Mosquitto Broker) |
| Frontend | Vanilla HTML, CSS, JavaScript |
| Fonts | Space Mono, DM Sans (Google Fonts) |

---

## 🔌 IoT Hardware Architecture

```
Physical Sensors
    │
    ▼
Arduino Uno + ESP8266 (Wi-Fi)
    │
    ▼
MQTT Broker (Mosquitto) → Topic: agro/node/001
    │
    ▼
TensorFlow.js (In-Browser ML Inference)
    │
    ▼
AgroSphere Digital Twin Dashboard
```

**Sensors used:**
- 💧 Capacitive Soil Moisture Sensor (Analog A0)
- 🌡️ DHT11 — Temperature & Humidity (Digital, I2C)
- ☀️ LDR — Light Intensity (Analog A0)
- 🔋 INA219 — Battery/Power Monitor

**Output:**
- 💧 Relay module connected to irrigation pump (Digital OUT D7)

---

## 🧠 ML Model

The TensorFlow.js model runs entirely **in the browser** with no server needed. It takes live sensor readings as input and outputs:

- **Health Classification** — Healthy / Moderate Stress / Critical
- **Yield Forecast** — Estimated kg per hectare
- **Irrigation Recommendation** — Water now / Hold / Optimal

---

## 📁 Project Structure

```
Agrosphere/
└── AgroSphere.html     ← Complete application (HTML + CSS + JS + ML)
```

All libraries are loaded via CDN. No build step, no dependencies to install.

---

## ▶️ How to Run

1. Clone or download the repository:
   ```bash
   git clone https://github.com/aryandotexe30/Agrosphere---Digital-Twin-on-Smart-Farming-using-IoT-and-ML.git
   ```

2. Open `AgroSphere.html` in any modern browser (Chrome recommended):
   ```
   Double-click AgroSphere.html
   ```

3. Allow location/network access if prompted (for live weather data).

> **Note:** For live IoT data, configure your Arduino + ESP8266 to publish to your MQTT broker on topic `agro/node/001`. The dashboard simulates sensor data by default.

---

## 🌍 Real-World Integration

To connect real hardware:

1. Flash Arduino Uno with sensor reading code (Serial output at 9600 baud)
2. Configure ESP8266 with your Wi-Fi credentials and MQTT broker IP
3. Update the MQTT broker address in `AgroSphere.html`
4. The Digital Twin will sync automatically with your physical farm node

---

## 📍 Location

**SRMIST Kattankulathur, Tamil Nadu, India**
Live weather data is fetched for this location via Open-Meteo API.

---

## 🖼️ Preview

| Dashboard | Architecture |
|---|---|
| 3D crop render with live sensor sync | Full hardware-software system diagram |
| ML health/yield/irrigation inference | IoT pipeline from sensor to twin |

---

## 🙋 Author

**Aryan** — [@aryandotexe30](https://github.com/aryandotexe30)

---

## 📄 License

This project is open source. Feel free to use, modify, and build on it.

---

> *AgroSphere bridges the physical farm and the digital world — giving every farmer the power of real-time intelligence.*
