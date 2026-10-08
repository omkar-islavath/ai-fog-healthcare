"""
Fog Node Entity Class
Encapsulates:
- Local 4-Agent Cluster (Monitoring, Security, Decision, Resource)
- AES-256-GCM Cryptographic Subsystem
- AI Vital & Security Model Inference Engines
- Local Caching & SQLite Storage
- Peer-to-Peer Task Offloading to neighboring Fog Nodes
"""

from typing import Dict, Any, List, Optional
from core.models import SensorPacket, FogNodeStatus
from core.crypto import SecurityCryptoEngine
from core.database import HealthcareDatabase
from ai.vital_classifier import VitalSignAIClassifier
from ai.threat_detector import CyberThreatDetector
from agents.base_agent import AgentMessageBus
from agents.monitoring_agent import MonitoringAgent
from agents.security_agent import SecurityAgent
from agents.decision_agent import DecisionAgent
from agents.resource_agent import ResourceAgent


class FogNode:
    def __init__(
        self,
        node_id: str,
        node_name: str,
        location: str,
        bus: AgentMessageBus,
        db: HealthcareDatabase,
        crypto: SecurityCryptoEngine,
        vital_ai: VitalSignAIClassifier,
        threat_ai: CyberThreatDetector,
        neighbor_nodes: Optional[List[str]] = None
    ):
        self.node_id = node_id
        self.node_name = node_name
        self.location = location
        self.bus = bus
        self.db = db
        self.crypto = crypto
        self.vital_ai = vital_ai
        self.threat_ai = threat_ai
        self.neighbor_nodes = neighbor_nodes or []

        # Instantiate Local Multi-Agents for this Fog Node
        self.monitoring_agent = MonitoringAgent(self.node_id, self.bus)
        self.security_agent = SecurityAgent(self.node_id, self.bus, self.crypto, self.threat_ai, self.db)
        self.decision_agent = DecisionAgent(self.node_id, self.bus, self.vital_ai, self.db)
        self.resource_agent = ResourceAgent(self.node_id, self.node_name, self.location, self.bus, self.db, self.neighbor_nodes)

    def ingest_sensor_packet(self, packet: SensorPacket) -> Dict[str, Any]:
        """
        Entrypoint for incoming IoT Sensor Telemetry packets at this Fog Node.
        """
        # Monitoring Agent handles raw packet ingestion & noise filtering
        self.monitoring_agent.send_message(
            receiver=f"MonitoringAgent_{self.node_id}",
            action="INGEST_SENSOR_PACKET",
            payload=packet.model_dump()
        )

        # Trigger adaptive computing resource monitoring
        self.resource_agent.adapt_resources()

        return {
            "status": "ACCEPTED_FOR_FOG_PROCESSING",
            "node_id": self.node_id,
            "packet_id": packet.packet_id
        }

    def get_status(self) -> FogNodeStatus:
        return self.resource_agent.get_node_metrics()

    def get_agents_status(self) -> List[Dict[str, Any]]:
        return [
            self.monitoring_agent.get_status(),
            self.security_agent.get_status(),
            self.decision_agent.get_status(),
            self.resource_agent.get_status()
        ]
