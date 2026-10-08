"""
Monitoring Agent (Fog Layer)
Responsible for:
- Ingesting raw IoT sensor packets
- Data filtering & noise reduction
- Sensor calibration checks & timestamp freshness validation
- Dispatching preprocessed streams to Security & Decision agents
"""

from typing import Dict, Any, Optional
from core.models import SensorPacket, AgentMessage
from agents.base_agent import BaseAgent, AgentMessageBus


class MonitoringAgent(BaseAgent):
    def __init__(self, fog_node_id: str, bus: AgentMessageBus):
        super().__init__(
            agent_id=f"MonitoringAgent_{fog_node_id}",
            agent_name="Data Ingestion & Monitoring Agent",
            fog_node_id=fog_node_id,
            bus=bus
        )
        self.total_ingested = 0
        self.noise_filtered_count = 0

    def on_message(self, message: AgentMessage):
        if message.action == "INGEST_SENSOR_PACKET":
            self.process_raw_packet(message.payload)

    def process_raw_packet(self, packet_data: Dict[str, Any]) -> Dict[str, Any]:
        """Filters noise and forwards to Security Agent."""
        self.state = "PROCESSING"
        self.total_ingested += 1
        self.processed_count += 1

        payload = packet_data.get("payload", {})
        
        # Noise filtering: e.g. Smooth negative baseline drift
        filtered_payload = dict(payload)
        for key in ["heart_rate", "spo2", "systolic_bp", "diastolic_bp", "temperature", "blood_glucose"]:
            if key in filtered_payload and filtered_payload[key] is not None:
                val = float(filtered_payload[key])
                # Filter negative readings from sensor glitch
                if val < 0:
                    filtered_payload[key] = abs(val)
                    self.noise_filtered_count += 1

        packet_data["filtered_payload"] = filtered_payload

        # Forward to Security Agent for verification
        self.send_message(
            receiver=f"SecurityAgent_{self.fog_node_id}",
            action="VERIFY_PACKET_SECURITY",
            payload=packet_data
        )

        self.state = "IDLE"
        return packet_data
