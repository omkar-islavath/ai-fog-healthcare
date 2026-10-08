"""
IoT & IoMT Smart Healthcare Device Simulator
Simulates:
- Smart Wearable ECG Patch (Heart Rate, Arrhythmia metric)
- Smart Pulse Oximeter (SpO2, Perfusion index)
- Connected Blood Pressure Monitor (Systolic, Diastolic)
- Continuous Glucose Monitor (CGM)
- Bedside Environmental & Respiration Sensor
"""

import time
import uuid
import json
import random
import numpy as np
from typing import Dict, Any, List, Optional
from core.models import SensorPacket, SensorType, PatientVitals
from core.crypto import SecurityCryptoEngine


class PatientProfile:
    def __init__(
        self,
        patient_id: str,
        name: str,
        age: int,
        department: str,
        base_hr: float = 75.0,
        base_spo2: float = 98.0,
        base_sbp: float = 120.0,
        base_dbp: float = 80.0,
        base_temp: float = 36.8,
        base_glucose: float = 100.0,
        base_rr: float = 16.0,
        condition_tendency: str = "STABLE"
    ):
        self.patient_id = patient_id
        self.name = name
        self.age = age
        self.department = department
        self.base_hr = base_hr
        self.base_spo2 = base_spo2
        self.base_sbp = base_sbp
        self.base_dbp = base_dbp
        self.base_temp = base_temp
        self.base_glucose = base_glucose
        self.base_rr = base_rr
        self.condition_tendency = condition_tendency  # STABLE, ARRHYTHMIA, HYPOXIA, HYPERTENSIVE

    def generate_current_vitals(self) -> Dict[str, Any]:
        """Generates realistic physiological reading with dynamic natural fluctuation."""
        now = time.time()
        # Sine wave breathing and cardiac pulse variation
        sin_wave = np.sin(now * 1.5) * 3.5
        cos_wave = np.cos(now * 0.8) * 2.0
        rand_noise = np.random.uniform(-1.5, 1.5)

        hr = max(45.0, min(180.0, self.base_hr + sin_wave + rand_noise))
        spo2 = min(100.0, max(75.0, self.base_spo2 + (np.sin(now * 0.5) * 0.8) + np.random.uniform(-0.3, 0.3)))
        sbp = max(80.0, min(230.0, self.base_sbp + cos_wave + np.random.uniform(-2.0, 2.0)))
        dbp = max(50.0, min(140.0, self.base_dbp + (cos_wave * 0.6) + np.random.uniform(-1.0, 1.0)))
        temp = round(self.base_temp + (np.sin(now * 0.2) * 0.15) + np.random.uniform(-0.05, 0.05), 1)
        glucose = round(self.base_glucose + (np.cos(now * 0.1) * 3.0) + np.random.uniform(-1.0, 1.0), 1)
        rr = max(10.0, min(35.0, self.base_rr + (sin_wave * 0.4) + np.random.uniform(-0.5, 0.5)))

        # Dynamic clinical events
        if self.condition_tendency == "ARRHYTHMIA":
            if (int(now) % 8) < 4:
                hr += 45.0  # Tachycardia episode
        elif self.condition_tendency == "HYPOXIA":
            if (int(now) % 10) < 5:
                spo2 -= 8.5  # Hypoxia episode
                rr += 8.0
        elif self.condition_tendency == "HYPERTENSIVE":
            if (int(now) % 12) < 6:
                sbp += 55.0  # BP surge
                dbp += 28.0

        return {
            "patient_id": self.patient_id,
            "patient_name": self.name,
            "age": self.age,
            "department": self.department,
            "heart_rate": round(float(hr), 1),
            "spo2": round(float(spo2), 1),
            "systolic_bp": round(float(sbp), 1),
            "diastolic_bp": round(float(dbp), 1),
            "temperature": float(temp),
            "blood_glucose": float(glucose),
            "respiratory_rate": round(float(rr), 1),
            "bed_motion_score": round(random.uniform(0.1, 1.8), 2),
            "timestamp": now
        }


class IoMTSensorDevice:
    def __init__(
        self,
        sensor_id: str,
        sensor_type: SensorType,
        patient: PatientProfile,
        crypto: SecurityCryptoEngine,
        target_fog_node: str = "FogNode-01"
    ):
        self.sensor_id = sensor_id
        self.sensor_type = sensor_type
        self.patient = patient
        self.crypto = crypto
        self.target_fog_node = target_fog_node

    def produce_telemetry_packet(self) -> SensorPacket:
        """Produces an encrypted, HMAC-signed, Zero-Trust authenticated sensor packet."""
        vitals = self.patient.generate_current_vitals()
        nonce = str(uuid.uuid4())
        timestamp = time.time()

        # Generate Zero-Trust token
        token = self.crypto.generate_device_token(self.sensor_id, self.patient.patient_id)

        # Generate cryptographic HMAC over payload
        payload_str = json.dumps(vitals, sort_keys=True)
        signature = self.crypto.generate_hmac(payload_str)

        packet = SensorPacket(
            packet_id=f"PKT_{uuid.uuid4().hex[:8]}",
            sensor_id=self.sensor_id,
            sensor_type=self.sensor_type,
            patient_id=self.patient.patient_id,
            payload=vitals,
            timestamp=timestamp,
            nonce=nonce,
            signature=signature,
            device_token=token,
            fog_node_target=self.target_fog_node
        )
        return packet
