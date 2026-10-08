"""
Cyber-Security Attack Injection Simulator
Allows live demonstration and testing of threat vectors:
1. DoS / Packet Flooding Attack
2. Data Tampering / Man-in-the-Middle Attack
3. Sensor Identity Spoofing & Rogue Devices
4. Replay Attack
"""

import time
import uuid
import json
from typing import List, Dict, Any
from core.models import SensorPacket, SensorType, ThreatType
from core.crypto import SecurityCryptoEngine


class SecurityAttackInjector:
    def __init__(self, crypto: SecurityCryptoEngine):
        self.crypto = crypto

    def create_dos_flood(self, target_sensor_id: str, count: int = 25, target_fog_node: str = "FogNode-01") -> List[SensorPacket]:
        """Generates a burst of packets within milliseconds to simulate DoS Flooding."""
        packets = []
        base_time = time.time()
        for i in range(count):
            pkt = SensorPacket(
                packet_id=f"DOS_PKT_{uuid.uuid4().hex[:8]}",
                sensor_id=target_sensor_id,
                sensor_type=SensorType.ECG_HEART_RATE,
                patient_id="P-101",
                payload={"heart_rate": 80.0, "timestamp": base_time},
                timestamp=base_time,
                nonce=str(uuid.uuid4()),
                signature=self.crypto.generate_hmac(json.dumps({"heart_rate": 80.0, "timestamp": base_time}, sort_keys=True)),
                device_token=self.crypto.generate_device_token(target_sensor_id, "P-101"),
                fog_node_target=target_fog_node
            )
            packets.append(pkt)
        return packets

    def create_tampered_packet(
        self,
        target_sensor_id: str,
        tamper_key: str = "heart_rate",
        tamper_value: float = 480.0,
        target_fog_node: str = "FogNode-01"
    ) -> SensorPacket:
        """Simulates Man-in-the-Middle tampering: payload altered after HMAC signature generation."""
        original_payload = {"patient_id": "P-101", "heart_rate": 75.0, "spo2": 98.0}
        orig_sig = self.crypto.generate_hmac(json.dumps(original_payload, sort_keys=True))
        
        # Attacker injects fake value without correct HMAC secret key
        tampered_payload = dict(original_payload)
        tampered_payload[tamper_key] = tamper_value

        return SensorPacket(
            packet_id=f"TAMPER_{uuid.uuid4().hex[:8]}",
            sensor_id=target_sensor_id,
            sensor_type=SensorType.ECG_HEART_RATE,
            patient_id="P-101",
            payload=tampered_payload,
            timestamp=time.time(),
            nonce=str(uuid.uuid4()),
            signature=orig_sig,  # Will fail verification on tampered content
            device_token=self.crypto.generate_device_token(target_sensor_id, "P-101"),
            fog_node_target=target_fog_node
        )

    def create_spoofed_sensor_packet(
        self,
        rogue_sensor_id: str = "ROGUE_SENSOR_0x99",
        target_fog_node: str = "FogNode-01"
    ) -> SensorPacket:
        """Simulates Rogue/Unauthenticated sensor injecting fake data with invalid token."""
        payload = {"patient_id": "P-101", "heart_rate": 90.0, "spo2": 97.0}
        return SensorPacket(
            packet_id=f"SPOOF_{uuid.uuid4().hex[:8]}",
            sensor_id=rogue_sensor_id,
            sensor_type=SensorType.ECG_HEART_RATE,
            patient_id="P-101",
            payload=payload,
            timestamp=time.time(),
            nonce=str(uuid.uuid4()),
            signature="INVALID_FORGED_SIGNATURE_0xDEADBEEF",
            device_token="FORGED_EXPIRED_OR_INVALID_TOKEN",
            fog_node_target=target_fog_node
        )

    def create_replay_packet(self, original_packet: SensorPacket) -> SensorPacket:
        """Simulates Replay attack by re-transmitting an old packet with identical nonce & signature."""
        replayed = SensorPacket(
            packet_id=f"REPLAY_{uuid.uuid4().hex[:8]}",
            sensor_id=original_packet.sensor_id,
            sensor_type=original_packet.sensor_type,
            patient_id=original_packet.patient_id,
            payload=original_packet.payload,
            timestamp=original_packet.timestamp - 45.0,  # 45 seconds stale
            nonce=original_packet.nonce,                 # Reused nonce
            signature=original_packet.signature,
            device_token=original_packet.device_token,
            fog_node_target=original_packet.fog_node_target
        )
        return replayed
