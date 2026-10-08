# SecureFog Health 🏥🛡️
**AI-Driven Multi-Agent Adaptive Fog Computing Framework for Secure Smart Healthcare**

A lightweight, real-time IoMT (Internet of Medical Things) framework that combines **Adaptive Fog Computing**, **Multi-Agent Systems (MAS)**, **Clinical AI Triage**, and **Zero-Trust Cyber-Security Defense**.

---

## ⚡ Features

* 🩺 **Real-Time Patient Vitals:** Live streaming and AI triage (Normal, Warning, Emergency) for multi-parameter physiological telemetry (ECG, SpO2, Blood Pressure, Glucose).
* 🛡️ **Cyber-Attack Detection Lab:** AI detection and dynamic firewall quarantine against **DoS Floods**, **Data Tampering (MitM)**, **Rogue Sensor Spoofing**, and **Replay Attacks**.
* ⚡ **Adaptive Fog Computing:** Dynamic sensor sampling rate scaling (Hz) and peer-to-peer task offloading between fog nodes under high load.
* 🔒 **HIPAA Privacy Preservation:** Cryptographic pseudonymization (SHA-256 salted hashes) and AES-256-GCM authenticated encryption before cloud synchronization.
* 🤖 **Multi-Agent Bus:** 4 autonomous local agents (`Monitoring`, `Security`, `Decision`, `Resource`) collaborating over an asynchronous message bus.

---

## 🚀 Quick Start

### 1. Prerequisites
* Python 3.10 or higher
* Git

### 2. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/ai-fog-healthcare.git
cd ai-fog-healthcare
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Automated Tests (15 Tests)
```bash
python -m pytest tests/test_framework.py -v
```

### 5. Launch the Application
```bash
python run.py
```
Open your browser and navigate to: **`http://127.0.0.1:8000`**

---

## 📁 Project Structure

```
ai_fog_healthcare/
├── agents/             # Multi-Agent Architecture (Monitoring, Security, Decision, Resource)
├── ai/                 # Machine Learning Models (Random Forest Vital Triage & Threat Detector)
├── api/                # FastAPI Application & WebSocket Live Hub
├── cloud/              # Cloud Data Center & Global Storage
├── core/               # AES-256-GCM, HMAC-SHA256, Zero-Trust Engine, SQLite Database
├── simulator/          # IoMT Sensors & Attack Injection Simulator
├── static/             # CSS Stylesheets & JavaScript
├── templates/          # HTML5 Dashboard
├── tests/              # 15 Automated Pytest Verification Tests
├── requirements.txt    # Python Dependencies
├── run.py              # Application Launcher
└── README.md           # Documentation
```

---

## 🌐 Free Cloud Deployment (Render.com)

1. Create a **New Web Service** on [Render.com](https://render.com).
2. Connect your GitHub repository.
3. Set the following options:
   * **Runtime:** `Python 3`
   * **Build Command:** `pip install -r requirements.txt`
   * **Start Command:** `uvicorn api.app:app --host 0.0.0.0 --port $PORT`
   * **Plan:** `Free`
4. Click **Deploy Web Service**.
