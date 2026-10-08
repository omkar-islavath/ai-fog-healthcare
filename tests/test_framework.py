"""
Comprehensive Automated Test Suite for:
AI-Driven Multi-Agent Adaptive Fog Computing Framework for Secure Smart Healthcare
Department of CSE (Cyber Security) - CVR College of Engineering
"""

import pytest
import time
import uuid
import json
import os
import sys

# Add project root to sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from core.models import SensorPacket, SensorType, ThreatType, VitalTriageLevel, AttackSimulationConfig
from core.crypto import SecurityCryptoEngine
from core.database import HealthcareDatabase
from ai.vital_classifier import VitalSignAIClassifier
from ai.threat_detector import CyberThreatDetector
from agents.base_agent import AgentMessageBus
from agents.monitoring_agent import MonitoringAgent
from agents.security_agent import SecurityAgent
from agents.decision_agent import DecisionAgent
from agents.resource_agent import ResourceAgent
from agents.cloud_coordinator_agent import CloudCoordinatorAgent
from fog_node import FogNode
from simulator.iot_devices import PatientProfile, IoMTSensorDevice
from simulator.attack_injector import SecurityAttackInjector
from cloud.cloud_server import CloudDataCenter
from fastapi.testclient import TestClient
from api.app import app


@pytest.fixture
def crypto_engine():
    return SecurityCryptoEngine()


@pytest.fixture
def temp_db(tmp_path):
    db_file = str(tmp_path / "test_fog_healthcare.db")
    return HealthcareDatabase(db_file)


@pytest.fixture
def vital_classifier():
    return VitalSignAIClassifier()


@pytest.fixture
def threat_detector():
    return CyberThreatDetector(flood_rate_threshold_hz=10.0, timestamp_skew_max_sec=5.0)


# =========================================================================
# 1. Cryptography & Zero-Trust Security Tests
# =========================================================================

def test_aes_256_gcm_encryption_decryption(crypto_engine):
    """Verifies AES-256-GCM symmetric authenticated encryption/decryption roundtrip."""
    sample_data = {
        "patient_id": "P-101",
        "heart_rate": 78.5,
        "spo2": 98.2,
        "systolic_bp": 122.0
    }
    cipher_b64, nonce_b64, tag_b64 = crypto_engine.encrypt_json(sample_data)
    assert cipher_b64 != ""
    assert nonce_b64 != ""
    assert tag_b64 != ""

    decrypted = crypto_engine.decrypt_json(cipher_b64, nonce_b64, tag_b64)
    assert decrypted["patient_id"] == "P-101"
    assert decrypted["heart_rate"] == 78.5
    assert decrypted["spo2"] == 98.2


def test_aes_gcm_tamper_detection(crypto_engine):
    """Verifies AES-256-GCM authentication fails if ciphertext or tag is modified."""
    sample_data = {"patient_id": "P-101", "heart_rate": 80.0}
    cipher_b64, nonce_b64, tag_b64 = crypto_engine.encrypt_json(sample_data)
    
    # Tamper with the tag
    tampered_tag = ("A" * (len(tag_b64) - 2)) + "=="
    with pytest.raises(ValueError):
        crypto_engine.decrypt_json(cipher_b64, nonce_b64, tampered_tag)


def test_hmac_sha256_signature(crypto_engine):
    """Verifies HMAC-SHA256 data integrity check."""
    payload = json.dumps({"patient_id": "P-101", "heart_rate": 75}, sort_keys=True)
    sig = crypto_engine.generate_hmac(payload)
    assert crypto_engine.verify_hmac(payload, sig) is True

    # Modified payload must fail HMAC check
    tampered_payload = json.dumps({"patient_id": "P-101", "heart_rate": 180}, sort_keys=True)
    assert crypto_engine.verify_hmac(tampered_payload, sig) is False


def test_zero_trust_device_token(crypto_engine):
    """Verifies Zero-Trust dynamic device token generation, validity, and rejection."""
    token = crypto_engine.generate_device_token("SENS-ECG-101", "P-101", expiry_seconds=60)
    assert crypto_engine.verify_device_token(token, "SENS-ECG-101") is True
    # Wrong sensor ID should fail
    assert crypto_engine.verify_device_token(token, "SENS-SPOOF-999") is False


def test_hipaa_privacy_anonymization(crypto_engine):
    """Verifies HIPAA/GDPR data masking before cloud sync."""
    vitals = {
        "patient_id": "P-99824",
        "patient_name": "John Doe",
        "age": 47,
        "heart_rate": 82.0,
        "spo2": 97.5
    }
    anonymized = crypto_engine.anonymize_patient_record(vitals)
    assert "P-99824" not in anonymized["patient_id"]
    assert anonymized["patient_id"].startswith("ANON_")
    assert anonymized["patient_name"] == "ANONYMIZED_SUBJECT"
    assert anonymized["age_group"] == "40-49"
    assert "age" not in anonymized
    assert anonymized["heart_rate"] == 82.0


# =========================================================================
# 2. AI Vital Sign Classification & Triage Tests
# =========================================================================

def test_vital_ai_normal_condition(vital_classifier):
    """Tests normal healthy physiological state classification."""
    normal_vitals = {
        "heart_rate": 72.0,
        "spo2": 98.5,
        "systolic_bp": 118.0,
        "diastolic_bp": 78.0,
        "temperature": 36.8,
        "blood_glucose": 95.0,
        "respiratory_rate": 15.0
    }
    result = vital_classifier.evaluate_vitals(normal_vitals)
    assert result["triage_level"] == VitalTriageLevel.NORMAL
    assert result["is_emergency"] is False


def test_vital_ai_tachycardia_emergency(vital_classifier):
    """Tests severe Arrhythmia / Tachycardia emergency triage."""
    crisis_vitals = {
        "heart_rate": 165.0,
        "spo2": 94.0,
        "systolic_bp": 130.0,
        "diastolic_bp": 85.0,
        "temperature": 37.0,
        "blood_glucose": 110.0,
        "respiratory_rate": 24.0
    }
    result = vital_classifier.evaluate_vitals(crisis_vitals)
    assert result["triage_level"] == VitalTriageLevel.CRITICAL_EMERGENCY
    assert result["is_emergency"] is True
    assert any("Tachycardia" in m for m in result["abnormal_metrics"])


def test_vital_ai_hypoxemia_emergency(vital_classifier):
    """Tests acute respiratory distress / Hypoxemia triage."""
    hypoxia_vitals = {
        "heart_rate": 118.0,
        "spo2": 78.0,
        "systolic_bp": 115.0,
        "diastolic_bp": 75.0,
        "temperature": 37.2,
        "blood_glucose": 105.0,
        "respiratory_rate": 32.0
    }
    result = vital_classifier.evaluate_vitals(hypoxia_vitals)
    assert result["triage_level"] == VitalTriageLevel.CRITICAL_EMERGENCY
    assert any("Hypoxia" in m for m in result["abnormal_metrics"])


# =========================================================================
# 3. AI Cyber Threat Detection Tests
# =========================================================================

def test_ai_detects_data_tampering(threat_detector):
    """Verifies AI detects Man-in-the-Middle payload tampering."""
    is_threat, alert = threat_detector.analyze_packet(
        sensor_id="SENS-ECG-101",
        packet_time=time.time(),
        nonce="NONCE-12345",
        token_valid=True,
        hmac_valid=False,  # Signature tampered
        payload_data={"heart_rate": 78.0}
    )
    assert is_threat is True
    assert alert.threat_type == ThreatType.DATA_TAMPERING
    assert alert.severity == "CRITICAL"


def test_ai_detects_dos_packet_flood(threat_detector):
    """Verifies AI detects volumetric DoS flooding."""
    now = time.time()
    sensor_id = "SENS-FLOOD-01"
    
    # Blast 20 packets in rapid succession
    threat_found = False
    for _ in range(20):
        is_threat, alert = threat_detector.analyze_packet(
            sensor_id=sensor_id,
            packet_time=now,
            nonce=str(uuid.uuid4()),
            token_valid=True,
            hmac_valid=True,
            payload_data={"heart_rate": 75.0}
        )
        if is_threat and alert.threat_type == ThreatType.DOS_FLOOD:
            threat_found = True
            break
            
    assert threat_found is True


def test_ai_detects_sensor_spoofing(threat_detector):
    """Verifies AI intercepts rogue unauthenticated sensor with invalid token."""
    is_threat, alert = threat_detector.analyze_packet(
        sensor_id="ROGUE_SENSOR_99",
        packet_time=time.time(),
        nonce="NONCE-SP-1",
        token_valid=False,  # Unauthenticated
        hmac_valid=False,
        payload_data={"heart_rate": 80.0}
    )
    assert is_threat is True
    assert alert.threat_type in [ThreatType.SENSOR_SPOOFING, ThreatType.DATA_TAMPERING]


def test_ai_detects_replay_attack(threat_detector):
    """Verifies AI intercepts duplicate nonce and stale timestamp replay."""
    now = time.time()
    nonce = "NONCE_REPLAY_TEST"
    
    # First valid receipt
    is_threat1, _ = threat_detector.analyze_packet(
        sensor_id="SENS-ECG-REPLAY",
        packet_time=now,
        nonce=nonce,
        token_valid=True,
        hmac_valid=True,
        payload_data={"heart_rate": 75.0}
    )
    assert is_threat1 is False

    # Second receipt with identical nonce -> Replay Attack
    is_threat2, alert2 = threat_detector.analyze_packet(
        sensor_id="SENS-ECG-REPLAY",
        packet_time=now,
        nonce=nonce,
        token_valid=True,
        hmac_valid=True,
        payload_data={"heart_rate": 75.0}
    )
    assert is_threat2 is True
    assert alert2.threat_type == ThreatType.REPLAY_ATTACK


# =========================================================================
# 4. Multi-Agent Coordination & Adaptive Fog Computing Tests
# =========================================================================

def test_multi_agent_pipeline_and_quarantine(temp_db, crypto_engine, vital_classifier, threat_detector):
    """Tests end-to-end local 4-agent collaboration on a Fog Node."""
    bus = AgentMessageBus()
    fog_node = FogNode(
        node_id="FogNode-Test",
        node_name="Test ICU Gateway",
        location="Lab",
        bus=bus,
        db=temp_db,
        crypto=crypto_engine,
        vital_ai=vital_classifier,
        threat_ai=threat_detector,
        neighbor_nodes=["FogNode-Neighbor"]
    )

    # Ingest a clean sensor packet
    patient = PatientProfile("P-T1", "Alice", 30, "ICU", base_hr=72, base_spo2=99)
    sensor = IoMTSensorDevice("SENS-T1", SensorType.ECG_HEART_RATE, patient, crypto_engine, "FogNode-Test")
    clean_packet = sensor.produce_telemetry_packet()

    resp = fog_node.ingest_sensor_packet(clean_packet)
    assert resp["status"] == "ACCEPTED_FOR_FOG_PROCESSING"

    # Ingest a tampered attack packet -> should trigger Security Agent quarantine
    injector = SecurityAttackInjector(crypto_engine)
    tampered_packet = injector.create_tampered_packet("SENS-T1", tamper_value=500.0, target_fog_node="FogNode-Test")
    fog_node.ingest_sensor_packet(tampered_packet)

    # Check database quarantine state
    assert temp_db.is_quarantined("SENS-T1") is True

    # Once quarantined, subsequent packets are blocked
    blocked = fog_node.security_agent.verify_and_route(clean_packet.model_dump())
    assert blocked is False


def test_adaptive_resource_scaling(temp_db, crypto_engine, vital_classifier, threat_detector):
    """Tests adaptive sampling rate scaling and neighbor task offloading under heavy load."""
    bus = AgentMessageBus()
    resource_agent = ResourceAgent(
        fog_node_id="FogNode-LoadTest",
        node_name="Load Test Node",
        location="Room 1",
        bus=bus,
        db=temp_db,
        neighbor_nodes=["FogNode-Backup"]
    )

    # Simulate CPU Spike / Attack Overload
    resource_agent.synthetic_cpu_boost = 50.0
    status = resource_agent.adapt_resources(threat_spike=True)
    
    # Adaptive computing must throttle sampling rate and offload to neighbor
    assert status["sampling_rate_hz"] < 2.0
    assert resource_agent.offloaded_tasks_count > 0


# =========================================================================
# 5. FastAPI REST & Integration Tests
# =========================================================================

def test_api_endpoints():
    """Tests REST endpoints for status, vitals, alerts, fog metrics, and attack injection."""
    client = TestClient(app)

    # 1. System status
    r = client.get("/api/status")
    assert r.status_code == 200
    assert r.json()["status"] == "OPERATIONAL"

    # 2. Fog nodes status
    r = client.get("/api/fog-nodes")
    assert r.status_code == 200
    assert "FogNode-01" in r.json()

    # 3. Live attack injection
    attack_payload = {
        "attack_type": "DATA_TAMPERING",
        "target_sensor_id": "SENS-TEST-API",
        "target_fog_node": "FogNode-01",
        "intensity": 5,
        "tamper_metric": "heart_rate",
        "tamper_value": 450.0
    }
    r = client.post("/api/attack/inject", json=attack_payload)
    assert r.status_code == 200
    assert r.json()["status"] == "ATTACK_INJECTED"

    # 4. Cloud sync
    r = client.post("/api/cloud/sync")
    assert r.status_code == 200
    assert r.json()["status"] == "SUCCESS"
