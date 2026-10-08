"""
Resource Agent (Fog Layer)
Responsible for:
- Monitoring Fog Node CPU, Memory, Queue Latency and Throughput
- Adaptive Computing: Dynamic Sensor Sampling Rate Scaling (Hz)
- Dynamic Load Balancing & Task Offloading to Neighboring Fog Nodes
- Power-Aware and Workload-Aware Fog Resource Allocation
"""

import time
import psutil
from typing import Dict, Any, Optional, List
from agents.base_agent import BaseAgent, AgentMessageBus
from core.models import AgentMessage, FogNodeStatus
from core.database import HealthcareDatabase


class ResourceAgent(BaseAgent):
    def __init__(
        self,
        fog_node_id: str,
        node_name: str,
        location: str,
        bus: AgentMessageBus,
        db: HealthcareDatabase,
        neighbor_nodes: Optional[List[str]] = None
    ):
        super().__init__(
            agent_id=f"ResourceAgent_{fog_node_id}",
            agent_name="Adaptive Resource & Load Balancing Agent",
            fog_node_id=fog_node_id,
            bus=bus
        )
        self.node_name = node_name
        self.location = location
        self.db = db
        self.neighbor_nodes = neighbor_nodes or []
        
        # Adaptive Parameters
        self.current_sampling_rate_hz = 2.0  # Default 2 Hz (1 packet every 500ms)
        self.min_sampling_rate_hz = 0.5
        self.max_sampling_rate_hz = 4.0
        self.cpu_load_threshold_pct = 75.0
        
        # State counters
        self.offloaded_tasks_count = 0
        self.processed_packets_count = 0
        self.active_threats_blocked = 0
        self.synthetic_cpu_boost = 0.0

    def on_message(self, message: AgentMessage):
        if message.action == "SECURITY_THREAT_NOTIFICATION":
            self.active_threats_blocked += 1
            # Automatically throttle resources under attack
            self.adapt_resources(threat_spike=True)
        elif message.action == "CLINICAL_EMERGENCY_DETECTED":
            # For emergency patients, temporarily increase priority sampling rate
            self.current_sampling_rate_hz = min(self.max_sampling_rate_hz, 3.5)
        elif message.action == "OFFLOADED_TASK_RECEIVE":
            self.processed_packets_count += 1

    def adapt_resources(self, threat_spike: bool = False) -> Dict[str, Any]:
        """
        Dynamically adapts Fog compute parameters based on current workload.
        """
        self.state = "SCALING"
        real_cpu = psutil.cpu_percent(interval=None)
        effective_cpu = min(100.0, real_cpu + self.synthetic_cpu_boost)

        # 1. Check if overloaded
        is_overloaded = effective_cpu > self.cpu_load_threshold_pct or threat_spike
        
        if is_overloaded:
            # Reduce sampling rate to conserve fog compute bandwidth
            self.current_sampling_rate_hz = max(self.min_sampling_rate_hz, self.current_sampling_rate_hz * 0.7)
            # Trigger load offloading to a neighbor fog node if available
            if self.neighbor_nodes:
                target_neighbor = self.neighbor_nodes[0]
                self.offload_to_neighbor(target_neighbor, {"task_type": "BATCH_TELEMETRY_INFERENCE"})
        else:
            # Gradually restore optimal sampling rate
            if self.current_sampling_rate_hz < 2.0:
                self.current_sampling_rate_hz = min(2.0, self.current_sampling_rate_hz + 0.2)

        # Decay synthetic CPU boost
        if self.synthetic_cpu_boost > 0:
            self.synthetic_cpu_boost = max(0.0, self.synthetic_cpu_boost - 5.0)

        self.state = "IDLE"
        return {
            "effective_cpu": round(effective_cpu, 1),
            "sampling_rate_hz": round(self.current_sampling_rate_hz, 2),
            "offloaded_count": self.offloaded_tasks_count
        }

    def offload_to_neighbor(self, target_node_id: str, task_payload: Dict[str, Any]):
        """Offloads task to peer fog node to balance cluster workload."""
        self.offloaded_tasks_count += 1
        self.send_message(
            receiver=f"ResourceAgent_{target_node_id}",
            action="OFFLOADED_TASK_RECEIVE",
            payload={
                "source_node": self.fog_node_id,
                "target_node": target_node_id,
                "task": task_payload,
                "timestamp": time.time()
            }
        )

    def get_node_metrics(self) -> FogNodeStatus:
        cpu = min(100.0, psutil.cpu_percent(interval=None) + self.synthetic_cpu_boost)
        mem = psutil.virtual_memory().percent
        queue_latency = 1.2 + (cpu / 100.0) * 12.0  # Dynamic latency calculation (1.2ms to 13.2ms)
        
        status_str = "OPTIMAL"
        if cpu > 85.0:
            status_str = "CRITICAL"
        elif cpu > 60.0:
            status_str = "HIGH_LOAD"

        return FogNodeStatus(
            node_id=self.fog_node_id,
            node_name=self.node_name,
            location=self.location,
            cpu_utilization_pct=round(cpu, 1),
            memory_utilization_pct=round(mem, 1),
            active_connections=4,
            queue_latency_ms=round(queue_latency, 2),
            status=status_str,
            sampling_rate_hz=round(self.current_sampling_rate_hz, 2),
            offloaded_tasks_count=self.offloaded_tasks_count,
            processed_packets_count=self.processed_packets_count,
            active_threats_blocked=self.active_threats_blocked
        )
