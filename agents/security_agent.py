"""
Security Agent (Fog Layer)
Responsible for:
- Zero-Trust Cryptographic Token and Signature Verification
- Real-Time AI Threat Detection (DoS, Tampering, Spoofing, Replay)
- Dynamic Firewall Enforcement and Rogue Device Quarantine
- Publishing Security Alerts to local database and Cloud
"""

import time
from typing import Dict, Any, Optional
from agents.base_agent import BaseAgent, AgentMessageBus
from core.models import AgentMessage, SecurityAlert, ThreatType
from core.crypto import SecurityCryptoEngine
from ai.threat_detector import CyberThreatDetector
from core.database import HealthcareDatabase


class SecurityAgent(BaseAgent):
    def __init__(
        self,
        fog_node_id: str,
        bus: AgentMessageBus,
        crypto: SecurityCryptoEngine,
        detector: CyberThreatDetector,
        db: HealthcareDatabase
    ):
        super().__init__(
            agent_id=f"SecurityAgent_{fog_node_id}",
            agent_name="Cyber-Security & Anomaly Detection Agent",
            fog_node_id=fog_node_id,
            bus=bus
        )
        self.crypto = crypto
        self.detector = detector
        self.db = db
        self.threats_blocked = 0

    def on_message(self, message: AgentMessage):
        if message.action == "VERIFY_PACKET_SECURITY":
            self.verify_and_route(message.payload)

    def verify_and_route(self, packet_data: Dict[str, Any]) -> bool:
        self.state = "PROCESSING"
        self.processed_count += 1

        sensor_id = packet_data.get("sensor_id", "UNKNOWN_SENSOR")
        patient_id = packet_data.get("patient_id", "UNKNOWN_PATIENT")
        payload = packet_data.get("filtered_payload", packet_data.get("payload", {}))
        nonce = packet_data.get("nonce", "")
        packet_time = packet_data.get("timestamp", time.time())
        token = packet_data.get("device_token", "")
        signature = packet_data.get("signature", "")

        # 1. Check if device is already quarantined
        if self.db.is_quarantined(sensor_id):
            self.state = "ALERTING"
            self.threats_blocked += 1
            # Drop packet immediately
            return False

        # 2. Cryptographic checks
        token_valid = self.crypto.verify_device_token(token, sensor_id) if token else False
        
        # Verify HMAC signature over payload data
        import json
        payload_str = json.dumps(payload, sort_keys=True)
        hmac_valid = self.crypto.verify_hmac(payload_str, signature) if signature else False

        # 3. AI Cyber Threat Analysis
        is_threat, alert = self.detector.analyze_packet(
            sensor_id=sensor_id,
            packet_time=packet_time,
            nonce=nonce,
            token_valid=token_valid,
            hmac_valid=hmac_valid,
            payload_data=payload,
            fog_node_id=self.fog_node_id
        )

        if is_threat and alert is not None:
            self.state = "ALERTING"
            self.threats_blocked += 1
            
            # Save alert to database
            self.db.log_security_alert(alert.model_dump())

            # Enforce automatic quarantine on critical/high threats
            if alert.severity in ["CRITICAL", "HIGH"]:
                self.db.quarantine_device(
                    sensor_id=sensor_id,
                    reason=f"{alert.threat_type.value}: {alert.description}",
                    fog_node_id=self.fog_node_id
                )

            # Notify Resource Agent and Cloud Management
            self.send_message(
                receiver=f"ResourceAgent_{self.fog_node_id}",
                action="SECURITY_THREAT_NOTIFICATION",
                payload=alert.model_dump()
            )
            self.send_message(
                receiver="CloudCoordinatorAgent",
                action="GLOBAL_SECURITY_ALERT",
                payload=alert.model_dump()
            )
            return False

        # If clean: forward payload to Decision Agent for clinical AI triage
        self.send_message(
            receiver=f"DecisionAgent_{self.fog_node_id}",
            action="CLINICAL_AI_EVALUATION",
            payload={
                "patient_id": patient_id,
                "sensor_id": sensor_id,
                "payload": payload,
                "timestamp": packet_time
            }
        )

        self.state = "IDLE"
        return True
