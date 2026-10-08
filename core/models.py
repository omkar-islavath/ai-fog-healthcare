"""
Data Models for AI-Driven Multi-Agent Adaptive Fog Computing Framework
Secure Smart Healthcare Domain
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class ThreatType(str, Enum):
    NONE = "NONE"
    DOS_FLOOD = "DOS_FLOOD"
    DATA_TAMPERING = "DATA_TAMPERING"
    SENSOR_SPOOFING = "SENSOR_SPOOFING"
    REPLAY_ATTACK = "REPLAY_ATTACK"
    UNAUTHORIZED_ACCESS = "UNAUTHORIZED_ACCESS"


class VitalTriageLevel(str, Enum):
    NORMAL = "NORMAL"
    WARNING = "WARNING"
    CRITICAL_EMERGENCY = "CRITICAL_EMERGENCY"


class SensorType(str, Enum):
    ECG_HEART_RATE = "ECG_HEART_RATE"
    PULSE_OXIMETER_SPO2 = "PULSE_OXIMETER_SPO2"
    BLOOD_PRESSURE = "BLOOD_PRESSURE"
    TEMPERATURE = "TEMPERATURE"
    GLUCOSE_MONITOR = "GLUCOSE_MONITOR"
    BED_SENSOR = "BED_SENSOR"


class PatientVitals(BaseModel):
    patient_id: str
    patient_name: str
    age: int
    department: str = "ICU"  # ICU, General Ward, Outpatient
    heart_rate: float = Field(..., description="Beats per minute (BPM)")
    spo2: float = Field(..., description="Blood Oxygen Saturation (%)")
    systolic_bp: float = Field(..., description="Systolic Blood Pressure (mmHg)")
    diastolic_bp: float = Field(..., description="Diastolic Blood Pressure (mmHg)")
    temperature: float = Field(..., description="Body Temperature (°C)")
    blood_glucose: float = Field(..., description="mg/dL")
    respiratory_rate: float = Field(16.0, description="Breaths per minute")
    bed_motion_score: float = Field(0.0, description="Patient movement index")
    timestamp: float = Field(default_factory=lambda: datetime.now().timestamp())


class SensorPacket(BaseModel):
    packet_id: str
    sensor_id: str
    sensor_type: SensorType
    patient_id: str
    payload: Dict[str, Any]
    timestamp: float = Field(default_factory=lambda: datetime.now().timestamp())
    nonce: str
    signature: str = ""
    device_token: str = ""
    fog_node_target: str = "FogNode-01"


class EncryptedPayload(BaseModel):
    packet_id: str
    sensor_id: str
    ciphertext_b64: str
    nonce_b64: str
    tag_b64: str
    hmac_sha256: str
    timestamp: float


class SecurityAlert(BaseModel):
    alert_id: str
    threat_type: ThreatType
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    source_sensor_id: str
    source_ip_mac: str
    fog_node_id: str
    description: str
    confidence_score: float
    mitigation_action: str  # e.g., "ISOLATE_SENSOR", "BLOCK_PACKET", "THROTTLE_PORT"
    timestamp: float = Field(default_factory=lambda: datetime.now().timestamp())


class ClinicalAlert(BaseModel):
    alert_id: str
    patient_id: str
    patient_name: str
    triage_level: VitalTriageLevel
    abnormal_metrics: List[str]
    diagnosis_flag: str
    confidence: float
    recommended_action: str
    fog_node_id: str
    timestamp: float = Field(default_factory=lambda: datetime.now().timestamp())


class FogNodeStatus(BaseModel):
    node_id: str
    node_name: str
    location: str
    cpu_utilization_pct: float
    memory_utilization_pct: float
    active_connections: int
    queue_latency_ms: float
    status: str  # OPTIMAL, HIGH_LOAD, CRITICAL, ISOLATED
    sampling_rate_hz: float
    offloaded_tasks_count: int
    processed_packets_count: int
    active_threats_blocked: int


class AgentMessage(BaseModel):
    message_id: str
    sender_agent: str
    receiver_agent: str
    action: str
    payload: Dict[str, Any]
    timestamp: float = Field(default_factory=lambda: datetime.now().timestamp())


class AttackSimulationConfig(BaseModel):
    attack_type: ThreatType
    target_sensor_id: str
    target_fog_node: str = "FogNode-01"
    intensity: int = 10  # number of packets or rate
    tamper_metric: Optional[str] = "heart_rate"
    tamper_value: Optional[float] = 300.0


class CloudSyncRecord(BaseModel):
    sync_id: str
    fog_node_id: str
    anonymized_patient_hash: str
    aggregated_vitals: Dict[str, float]
    triage_summary: str
    security_event_count: int
    timestamp: float = Field(default_factory=lambda: datetime.now().timestamp())
