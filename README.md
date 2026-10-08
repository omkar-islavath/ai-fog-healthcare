# AI-Driven Multi-Agent Adaptive Fog Computing Framework for Secure Smart Healthcare

**Institution:** CVR COLLEGE OF ENGINEERING  
**Department:** Department of Computer Science and Engineering (Cyber Security)  
**Program:** B.Tech CSE (CS) – IV Year I Semester  
**Course Project:** Project Stage-I / Stage-II Review  

### 👥 Project Team
* **P. SRINAG** – `23B81A62H8`
* **MOHD UMAIR** – `23B81A62J4`
* **T. VARSHITH** – `23B81A62J6`

### 🎓 Under the Guidance of
* **Dr. L. Roshini** – Sr. Assistant Professor, Department of CSE (Cyber Security), CVR College of Engineering

---

## 📌 1. Domain & Project Overview
* **Primary Domains:** Artificial Intelligence (AI) + Multi-Agent Systems (MAS) + Adaptive Fog Computing + Cyber Security + Internet of Medical Things (IoMT) / Smart Healthcare.
* **Core Problem:** High Cloud Dependency increases latency and exposes sensitive telemetry to transmission attacks; resource constraints at the edge lead to network congestion; IoMT devices are prime targets for DoS flooding, man-in-the-middle data tampering, replay attacks, and sensor spoofing.
* **Solution:** An autonomous, AI-driven, multi-agent adaptive fog computing architecture that processes and filters sensitive healthcare data near the patient, detects and isolates cyber threats in real-time, dynamically scales compute resources and offloads workload to neighbor nodes, and anonymizes data before cloud synchronization.

---

## 🏛️ 2. System Architecture & Component Mapping

```
+-----------------------------------------------------------------------------------+
|                                  CLOUD LAYER                                      |
|  +-------------------------------------+   +------------------------------------+  |
|  |          Cloud Data Center          |   |   Cloud Multi-Agent Management     |  |
|  | • Global HIPAA Storage & Analytics  |<->| • CloudCoordinatorAgent            |  |
|  | • Long-Term Knowledge Base          |   | • Global Threat Feed Distribution  |  |
|  | • Federated AI Model Aggregator     |   | • Global Policy & Cluster Health   |  |
|  +-------------------------------------+   +------------------------------------+  |
+------------------------------------------^----------------------------------------+
                                           | (Secure Encrypted Batch / Emergency Sync)
+------------------------------------------v----------------------------------------+
|                                  FOG LAYER                                        |
|  +---------------------------+  P2P Offload  +---------------------------+        |
|  | Fog Node 1 (ICU Gateway)  |<=============>| Fog Node 2 (Cardio Ward)  | ...    |
|  | +-----------------------+ |               | +-----------------------+ |        |
|  | | Monitoring Agent      | |               | | Monitoring Agent      | |        |
|  | | Security Agent (AI)   | |               | | Security Agent (AI)   | |        |
|  | | Decision Agent (AI)   | |               | | Decision Agent (AI)   | |        |
|  | | Resource Agent (Adapt)| |               | | Resource Agent (Adapt)| |        |
|  | +-----------------------+ |               | +-----------------------+ |        |
|  | • AES-256-GCM / SQLite  | |               | • AES-256-GCM / SQLite  | |        |
|  +---------------------------+               +---------------------------+        |
+------------------------------------------^----------------------------------------+
                                           | (Zero-Trust Token + HMAC Signed Stream)
+------------------------------------------v----------------------------------------+
|                         EDGE / IoMT SENSOR LAYER                                  |
|   [Wearable ECG]     [Pulse Oximeter]     [Smart BP Cuff]     [Continuous CGM]    |
|   (Heart Rate, HRV)    (SpO2, Perfusion)    (Systolic/Diastolic) (Blood Glucose)  |
+-----------------------------------------------------------------------------------+
```

### Local Multi-Agent Responsibilities (Fog Layer):
1. **Monitoring Agent (`MonitoringAgent`):**
   - Ingests raw telemetry from connected sensors.
   - Cleans baseline drift, eliminates negative anomalies/sensor noise, checks packet timestamp freshness, and standardizes payload schemas.
2. **Security Agent (`SecurityAgent`):**
   - Validates cryptographic HMAC-SHA256 signatures and dynamic Zero-Trust device tokens.
   - Executes the AI Cyber Threat Detector (detects DoS packet flooding, payload tampering, rogue sensor spoofing, replay attacks).
   - Automatically quarantines rogue sensors and updates the dynamic firewall table.
3. **Decision Agent (`DecisionAgent`):**
   - Executes the Clinical AI Vital Classifier (Random Forest + Isolation Forest ensemble).
   - Assesses multi-parameter physiological vitals: Heart Rate, SpO2, Systolic/Diastolic BP, Temperature, Blood Glucose, Respiration Rate.
   - Generates immediate emergency triage alerts (ICU, Doctor pager) for acute conditions (e.g., Tachycardia, Hypoxemia, Hypertensive Crisis, Sepsis).
4. **Resource Agent (`ResourceAgent`):**
   - Continuously monitors node CPU utilization, memory pressure, and queue delay.
   - Dynamically scales sensor sampling frequency (0.5 Hz to 4.0 Hz) based on load and clinical urgency.
   - Triggers peer-to-peer load offloading to neighboring fog nodes (e.g., `FogNode-01` offloading to `FogNode-02`) when load exceeds 75%.
5. **Cloud Coordinator Agent (`CloudCoordinatorAgent`):**
   - Aggregates anonymized, HIPAA-compliant patient records.
   - Dispatches global threat intelligence blacklists across all fog nodes.

---

## 🌟 3. Novel Features Over Existing Methods

| # | Novel Feature | Technical Implementation in this Project |
|---|---|---|
| **1** | **AI-Driven Decision Making** | Ensemble ML (Random Forest + Isolation Forest) for sub-millisecond clinical triage and arrhythmia/hypoxia detection at the fog layer. |
| **2** | **Multi-Agent Architecture** | Autonomous distributed agents (`Monitoring`, `Security`, `Decision`, `Resource`, `CloudCoordinator`) communicating via a lightweight async pub/sub bus. |
| **3** | **Adaptive Fog Computing** | Dynamic sampling rate adaptation (Hz) and automated peer-to-peer task offloading when CPU load exceeds 75%. |
| **4** | **Integrated Security & Zero-Trust** | Dynamic token validation, HMAC-SHA256 integrity checks, and AI threat classification for DoS, tampering, spoofing, and replay attacks. |
| **5** | **Privacy-Aware Processing** | HIPAA Safe Harbor-compliant cryptographic pseudonymization (SHA-256 salted hashing + age grouping) prior to cloud synchronization. |
| **6** | **Real-Time Ultra-Low Latency Response** | Local fog processing reduces latency to ~1.2 ms compared to 150+ ms for direct cloud transmission. |
| **7** | **Collaborative Agents** | Inter-agent message exchange enabling security events to trigger dynamic resource throttling and hospital ICU alerts. |

---

## 🔬 4. Post-2024 Literature Comparison

1. **Shah, B., et al. (2025).** *AI-Driven Fog-Edge Computing for IoMT Systems: Architecture and Use Cases.* Proceedings of the AAAI Symposium Series, 6(1), 42–48.
2. **Islam, U., et al. (2025).** *A hybrid fog-edge computing architecture for real-time health monitoring in IoMT systems with optimized latency and threat resilience.* Scientific Reports (Nature), 15, 25655.
3. **Fahd, K., Parvin, S., & Di Serio, A. (2025).** *Secure Fog Computing for Remote Health Monitoring with Data Prioritisation and AI-Based Anomaly Detection.* Sensors (MDPI), 25(23), 7329.
4. **Khan, A. A., et al. (2025).** *A lightweight scalable hybrid authentication framework for Internet of Medical Things (IoMT).* Scientific Reports, 15, 19856.
5. **Khan, U. H., et al. (2025).** *Secure edge-based IoMT framework for ICU monitoring with TinyML and post-quantum cryptography.* Scientific Reports, 15, 36195.

---

## 🚀 5. Quick Start & Execution Guide

### Prerequisites
* Python 3.10+ (Python 3.12 verified)
* Packages: `fastapi`, `uvicorn`, `scikit-learn`, `cryptography`, `pydantic`, `pytest`, `httpx`, `jinja2`, `psutil`, `numpy`, `pandas`

### Step 1: Run the Automated Test Suite
Run the 15-test automated verification suite:
```powershell
python -m pytest tests/test_framework.py -v
```
*Expected Result:* All 15 tests pass (100% pass rate).

### Step 2: Start the System & Live Dashboard
Launch the framework backend, simulator, and web dashboard with one command:
```powershell
python run.py
```
This starts the FastAPI server at `http://127.0.0.1:8000` and automatically launches your default web browser.

---

## 🖥️ 6. Interactive Web Dashboard Features

* **Live Telemetry Waveform (Chart.js):** Displays streaming Heart Rate (BPM) and SpO2 (%) in real time.
* **Patient Physiological Cards:** Displays multi-parameter vitals for 4 simulated patients (ICU, Cardiology, Pulmonary, General Ward) with green (NORMAL), amber (WARNING), and pulsing red (CRITICAL EMERGENCY) badges.
* **Cyber-Attack Injection Lab:**
  - Launch simulated attacks: **DoS Packet Flood**, **Data Tampering (MitM)**, **Rogue Sensor Spoofing**, and **Replay Attacks**.
  - Observe the Security Agent intercepting the attack, logging an incident, and placing the rogue device into the **Dynamic Quarantine / Firewall**.
* **Adaptive Computing Cluster:** Live CPU meters, latency monitors, adaptive sampling rates (Hz), and offloaded task counters across 3 collaborative fog nodes (`FogNode-01`, `FogNode-02`, `FogNode-03`).
* **Live Multi-Agent Message Bus Log:** Visual terminal showing inter-agent pub/sub communication in real-time.
* **One-Click Cloud Sync:** HIPAA-compliant anonymized sync button pushing local fog records to the central cloud repository.

---

## 🧠 7. Viva Voce & Review Q&A Guide

### Q1: Why use Fog Computing instead of pure Cloud Computing in Smart Healthcare?
> **Answer:** Pure cloud computing introduces high latency (100–300 ms), high bandwidth consumption, and single-point-of-failure risks during network outages. Fog computing places computational intelligence within meters of the patient (1–5 ms latency), enabling real-time detection of life-threatening cardiac arrest or hypoxia, and local containment of cyber-attacks without exposing raw data to the Internet.

### Q2: How does the Multi-Agent System (MAS) improve fault tolerance and adaptability?
> **Answer:** Instead of a monolithic codebase, tasks are divided among specialized autonomous agents (`Monitoring`, `Security`, `Decision`, `Resource`, `CloudCoordinator`). If the node is under a DoS flood, the `Security Agent` detects the attack and notifies the `Resource Agent` to throttle sampling rates and offload routine inference tasks to neighboring fog nodes (`FogNode-02`), preventing node crash.

### Q3: How is Patient Data Privacy preserved according to HIPAA/GDPR standards?
> **Answer:** Raw personally identifiable information (PII such as patient name, exact age, national ID) is never transmitted to the cloud. The framework uses salted SHA-256 cryptographic hashing (`ANON_xxxxxx`) and age bracket generalization (`40-49`) before cloud offloading, while symmetric AES-256-GCM encryption secures all inter-node communication.

### Q4: How does the AI Threat Detector identify Man-in-the-Middle (MitM) Tampering?
> **Answer:** Through a dual-verification mechanism:
> 1. **Cryptographic Integrity:** Every packet is signed with HMAC-SHA256. If a malicious actor alters payload values, the HMAC check fails.
> 2. **Physiological Anomaly AI:** The machine learning model flags physically impossible physiological jumps (e.g., Heart Rate jumping from 75 to 480 BPM in 200 ms) as data tampering.

---

## 📁 8. Project Directory Structure
```
ai_fog_healthcare/
├── agents/
│   ├── base_agent.py              # Async Pub/Sub Agent Message Bus & Base Class
│   ├── monitoring_agent.py        # Ingestion, Noise Filtering & Calibration Agent
│   ├── security_agent.py          # Zero-Trust, AI Threat Detection & Quarantine Agent
│   ├── decision_agent.py          # Clinical AI Inference & Emergency Triage Agent
│   ├── resource_agent.py          # Adaptive Sampling & Neighbor Offloading Agent
│   └── cloud_coordinator_agent.py # Global Policy & Cloud Sync Multi-Agent Manager
├── ai/
│   ├── vital_classifier.py        # ML Clinical Vital Triage (RandomForest + IsolationForest)
│   └── threat_detector.py         # ML Cyber Threat Detector (DoS, Tampering, Spoofing, Replay)
├── api/
│   └── app.py                     # FastAPI REST Endpoints & Real-Time WebSocket Hub
├── cloud/
│   └── cloud_server.py            # Central Cloud Data Center & Global Analytics
├── core/
│   ├── models.py                  # Pydantic Schemas for Vitals, Alerts, Nodes, Attacks
│   ├── crypto.py                  # AES-256-GCM, HMAC-SHA256, Zero-Trust, HIPAA Anonymization
│   └── database.py                # SQLite Local Fog & Cloud Ledger Database Engine
├── simulator/
│   ├── iot_devices.py             # IoMT Sensors (ECG, SpO2, BP, CGM) & Patients Simulator
│   └── attack_injector.py         # Live Attack Injector (DoS, MitM, Spoof, Replay)
├── static/
│   ├── css/style.css              # Custom Animations, Pulses, Glassmorphic Styling
│   └── js/dashboard.js            # Real-time WebSocket Client, Chart.js & Attack Controller
├── templates/
│   └── index.html                 # Modern Tailwind CSS Cyber-Healthcare Web Dashboard
├── tests/
│   └── test_framework.py          # 15 Automated Pytest Verification Tests
├── run.py                         # One-Command System Launcher
└── README.md                      # Comprehensive Technical Documentation
```
