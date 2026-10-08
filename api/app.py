"""
FastAPI Server & Real-Time WebSocket Hub for Multi-Agent Fog Healthcare Framework
"""

import asyncio
import os
import time
import json
import uuid
from typing import Dict, Any, List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from core.models import SensorPacket, SensorType, AttackSimulationConfig, ThreatType
from core.crypto import SecurityCryptoEngine
from core.database import HealthcareDatabase
from ai.vital_classifier import VitalSignAIClassifier
from ai.threat_detector import CyberThreatDetector
from agents.base_agent import AgentMessageBus
from fog_node import FogNode
from simulator.iot_devices import PatientProfile, IoMTSensorDevice
from simulator.attack_injector import SecurityAttackInjector
from cloud.cloud_server import CloudDataCenter

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: trigger IoT telemetry background task
    task = asyncio.create_task(iot_streaming_loop())
    yield
    # Shutdown
    task.cancel()

# Initialize FastAPI App with Lifespan
app = FastAPI(
    title="AI-Driven Multi-Agent Adaptive Fog Computing Framework for Secure Smart Healthcare",
    description="Smart Healthcare IoMT Framework with Multi-Agent Adaptive Fog Computing and Zero-Trust Security",
    version="1.0.0",
    lifespan=lifespan
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

templates = Jinja2Templates(directory=TEMPLATES_DIR)

# System Singletons
bus = AgentMessageBus()
db = HealthcareDatabase(os.path.join(BASE_DIR, "fog_healthcare.db"))
crypto = SecurityCryptoEngine()
vital_ai = VitalSignAIClassifier()
threat_ai = CyberThreatDetector()
cloud_center = CloudDataCenter(bus=bus, db=db, crypto=crypto)
attack_injector = SecurityAttackInjector(crypto=crypto)

# Instantiate 3 Collaborative Fog Nodes (ICU, Cardiology Ward, General Outpatient)
fog_nodes: Dict[str, FogNode] = {
    "FogNode-01": FogNode("FogNode-01", "ICU Fog Gateway", "ICU Ward B", bus, db, crypto, vital_ai, threat_ai, neighbor_nodes=["FogNode-02", "FogNode-03"]),
    "FogNode-02": FogNode("FogNode-02", "Cardiology Fog Gateway", "Cardio Ward 3", bus, db, crypto, vital_ai, threat_ai, neighbor_nodes=["FogNode-01", "FogNode-03"]),
    "FogNode-03": FogNode("FogNode-03", "Outpatient Fog Gateway", "Clinic Wing 1", bus, db, crypto, vital_ai, threat_ai, neighbor_nodes=["FogNode-01", "FogNode-02"])
}

# Simulated Patient Population
patients = [
    PatientProfile("P-101", "Sarah Jenkins", 58, "ICU", base_hr=74, base_spo2=98, base_sbp=122, base_dbp=80, condition_tendency="ARRHYTHMIA"),
    PatientProfile("P-102", "Rajesh Kumar", 64, "Cardiology Ward", base_hr=82, base_spo2=93, base_sbp=155, base_dbp=98, condition_tendency="HYPERTENSIVE"),
    PatientProfile("P-103", "Elena Rostova", 42, "Pulmonary ICU", base_hr=88, base_spo2=91, base_sbp=118, base_dbp=76, condition_tendency="HYPOXIA"),
    PatientProfile("P-104", "David Miller", 35, "General Ward", base_hr=72, base_spo2=99, base_sbp=115, base_dbp=75, condition_tendency="STABLE"),
]

# Simulated IoT Sensors mapped to patients & target fog nodes
sensors: List[IoMTSensorDevice] = [
    IoMTSensorDevice("SENS-ECG-101", SensorType.ECG_HEART_RATE, patients[0], crypto, "FogNode-01"),
    IoMTSensorDevice("SENS-SPO2-101", SensorType.PULSE_OXIMETER_SPO2, patients[0], crypto, "FogNode-01"),
    IoMTSensorDevice("SENS-BP-102", SensorType.BLOOD_PRESSURE, patients[1], crypto, "FogNode-02"),
    IoMTSensorDevice("SENS-SPO2-103", SensorType.PULSE_OXIMETER_SPO2, patients[2], crypto, "FogNode-01"),
    IoMTSensorDevice("SENS-CGM-104", SensorType.GLUCOSE_MONITOR, patients[3], crypto, "FogNode-03"),
]

# WebSocket Connection Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: Dict[str, Any]):
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception:
                self.disconnect(connection)

ws_manager = ConnectionManager()
is_simulator_running = True


live_patient_cache: Dict[str, Dict[str, Any]] = {}

# Background Task: Streaming IoT Data to Fog Nodes
async def iot_streaming_loop():
    while True:
        if is_simulator_running:
            for sensor in sensors:
                try:
                    packet = sensor.produce_telemetry_packet()
                    target_node = fog_nodes.get(sensor.target_fog_node, fog_nodes["FogNode-01"])
                    target_node.ingest_sensor_packet(packet)

                    # Update in-memory live patient cache with AI evaluation
                    eval_result = vital_ai.evaluate_vitals(packet.payload)
                    v_entry = dict(packet.payload)
                    v_entry["triage_level"] = eval_result["triage_level"].value
                    v_entry["fog_node_id"] = sensor.target_fog_node
                    live_patient_cache[sensor.patient.patient_id] = v_entry
                except Exception as e:
                    print(f"Error in sensor stream: {e}")
        
        # Periodic cloud routine sync
        if int(time.time()) % 15 == 0:
            recent = list(live_patient_cache.values())
            if recent:
                cloud_center.coordinator.send_message(
                    receiver="CloudCoordinatorAgent",
                    action="BATCH_FOG_SYNC",
                    payload={"fog_node_id": "FogNode-01", "records": recent}
                )

        # Broadcast real-time state to connected dashboard clients
        if ws_manager.active_connections:
            sec_alerts = db.get_recent_security_alerts(limit=5)
            clin_alerts = db.get_recent_clinical_alerts(limit=5)
            node_stats = {nid: node.get_status().model_dump() for nid, node in fog_nodes.items()}
            quarantined = db.get_quarantined_devices()

            payload = {
                "type": "TELEMETRY_UPDATE",
                "timestamp": time.time(),
                "vitals": list(live_patient_cache.values()),
                "security_alerts": sec_alerts,
                "clinical_alerts": clin_alerts,
                "fog_nodes": node_stats,
                "quarantined_devices": quarantined,
                "agent_messages": [m.model_dump() for m in bus.message_history[-10:]]
            }
            await ws_manager.broadcast(payload)

        await asyncio.sleep(0.9)





# --- API Routes ---

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/api/status")
async def get_system_status():
    return {
        "status": "OPERATIONAL",
        "project": "AI-Driven Multi-Agent Adaptive Fog Computing Framework for Secure Smart Healthcare",
        "college": "CVR College of Engineering - CSE(Cyber Security)",
        "fog_nodes_count": len(fog_nodes),
        "monitored_patients_count": len(patients),
        "active_sensors_count": len(sensors),
        "cloud_data_center": cloud_center.get_cloud_summary()
    }


class NewPatientRequest(BaseModel):
    name: str
    age: int
    department: str = "ICU"
    base_hr: float = 75.0
    base_spo2: float = 98.0
    base_sbp: float = 120.0
    base_dbp: float = 80.0
    condition_tendency: str = "STABLE"
    target_fog_node: str = "FogNode-01"

@app.post("/api/patients/add")
async def add_new_patient(req: NewPatientRequest):
    new_pid = f"P-{100 + len(patients) + 1}"
    new_patient = PatientProfile(
        patient_id=new_pid,
        name=req.name,
        age=req.age,
        department=req.department,
        base_hr=req.base_hr,
        base_spo2=req.base_spo2,
        base_sbp=req.base_sbp,
        base_dbp=req.base_dbp,
        condition_tendency=req.condition_tendency
    )
    patients.append(new_patient)
    
    # Attach new IoMT Sensor
    sensor_id = f"SENS-ECG-{new_pid[2:]}"
    new_sensor = IoMTSensorDevice(sensor_id, SensorType.ECG_HEART_RATE, new_patient, crypto, req.target_fog_node)
    sensors.append(new_sensor)
    
    return {
        "status": "SUCCESS",
        "message": f"Patient {req.name} ({new_pid}) admitted to {req.department} with active IoMT Sensor {sensor_id}.",
        "patient_id": new_pid,
        "sensor_id": sensor_id
    }

@app.get("/api/vitals/recent")
async def get_recent_vitals(limit: int = 30):
    return db.get_recent_vitals(limit=limit)


@app.get("/api/alerts/security")
async def get_security_alerts(limit: int = 20):
    return db.get_recent_security_alerts(limit=limit)


@app.get("/api/alerts/clinical")
async def get_clinical_alerts(limit: int = 20):
    return db.get_recent_clinical_alerts(limit=limit)


@app.get("/api/fog-nodes")
async def get_fog_nodes():
    res = {}
    for nid, node in fog_nodes.items():
        res[nid] = {
            "metrics": node.get_status().model_dump(),
            "agents": node.get_agents_status()
        }
    return res


@app.get("/api/quarantine/list")
async def get_quarantined():
    return db.get_quarantined_devices()


@app.post("/api/quarantine/unblock")
async def unblock_sensor(sensor_id: str):
    db.unquarantine_device(sensor_id)
    return {"status": "SUCCESS", "message": f"Sensor {sensor_id} unblocked and restored to active network."}


@app.post("/api/attack/inject")
async def inject_attack(config: AttackSimulationConfig):
    target_node = fog_nodes.get(config.target_fog_node, fog_nodes["FogNode-01"])
    now_ts = int(time.time())
    
    if config.attack_type == ThreatType.DOS_FLOOD:
        sensor_id = f"SENS-FLOOD-{now_ts % 1000:03d}"
        db.unquarantine_device(sensor_id)
        packets = attack_injector.create_dos_flood(sensor_id, count=config.intensity, target_fog_node=config.target_fog_node)
        target_node.resource_agent.synthetic_cpu_boost = 35.0  # Simulate CPU spike under flood
        for p in packets:
            target_node.ingest_sensor_packet(p)
        msg = f"Injected DoS Packet Flood ({config.intensity} pkts/sec) targeting {config.target_fog_node}."

    elif config.attack_type == ThreatType.DATA_TAMPERING:
        sensor_id = f"SENS-TAMPER-{now_ts % 1000:03d}"
        db.unquarantine_device(sensor_id)
        pkt = attack_injector.create_tampered_packet(
            sensor_id,
            tamper_key=config.tamper_metric or "heart_rate",
            tamper_value=config.tamper_value or 480.0,
            target_fog_node=config.target_fog_node
        )
        target_node.ingest_sensor_packet(pkt)
        msg = f"Injected Data Tampering (Heart Rate = {config.tamper_value or 480} BPM) targeting {config.target_fog_node}."

    elif config.attack_type == ThreatType.SENSOR_SPOOFING:
        sensor_id = f"ROGUE_SENSOR_0x{uuid.uuid4().hex[:4].upper()}"
        pkt = attack_injector.create_spoofed_sensor_packet(
            rogue_sensor_id=sensor_id,
            target_fog_node=config.target_fog_node
        )
        target_node.ingest_sensor_packet(pkt)
        msg = f"Injected Rogue Sensor Spoofing ({sensor_id}) without valid Zero-Trust token on {config.target_fog_node}."

    elif config.attack_type == ThreatType.REPLAY_ATTACK:
        sensor_id = f"SENS-REPLAY-{now_ts % 1000:03d}"
        db.unquarantine_device(sensor_id)
        dummy_patient = PatientProfile("P-999", "Replay Target", 50, "ICU")
        dummy_sensor = IoMTSensorDevice(sensor_id, SensorType.ECG_HEART_RATE, dummy_patient, crypto, config.target_fog_node)
        fresh_pkt = dummy_sensor.produce_telemetry_packet()
        target_node.ingest_sensor_packet(fresh_pkt)
        time.sleep(0.05)
        replay_pkt = attack_injector.create_replay_packet(fresh_pkt)
        target_node.ingest_sensor_packet(replay_pkt)
        msg = f"Injected Replay Attack with duplicate nonce & stale timestamp on {config.target_fog_node}."
    else:
        raise HTTPException(status_code=400, detail="Invalid attack type.")

    return {
        "status": "ATTACK_INJECTED",
        "attack_type": config.attack_type.value,
        "message": msg
    }


@app.post("/api/cloud/sync")
async def force_cloud_sync():
    vitals = db.get_recent_vitals(limit=10)
    for v in vitals:
        cloud_center.coordinator.send_message(
            receiver="CloudCoordinatorAgent",
            action="BATCH_FOG_SYNC",
            payload={"fog_node_id": v.get("fog_node_id", "FogNode-01"), "records": [v]}
        )
    return {"status": "SUCCESS", "message": f"Synced {len(vitals)} anonymized patient records to Cloud Data Center."}


@app.get("/api/cloud/summary")
async def get_cloud_summary():
    return cloud_center.get_cloud_summary()


@app.get("/api/agent-logs")
async def get_agent_logs():
    return [m.model_dump() for m in bus.message_history]


@app.websocket("/ws/stream")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # client heartbeat
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
