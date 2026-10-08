"""
Decision Agent (Fog Layer)
Responsible for:
- Real-Time AI Inference on Patient Physiological Vitals
- Patient Triage Classification (NORMAL, WARNING, CRITICAL_EMERGENCY)
- High-Priority Clinical Alert Generation for Healthcare Staff / ICU
- Local Caching and Privacy-Preserving Cloud Offload Triggering
"""

from typing import Dict, Any
from agents.base_agent import BaseAgent, AgentMessageBus
from core.models import AgentMessage, ClinicalAlert, VitalTriageLevel
from ai.vital_classifier import VitalSignAIClassifier
from core.database import HealthcareDatabase
from datetime import datetime


class DecisionAgent(BaseAgent):
    def __init__(
        self,
        fog_node_id: str,
        bus: AgentMessageBus,
        classifier: VitalSignAIClassifier,
        db: HealthcareDatabase
    ):
        super().__init__(
            agent_id=f"DecisionAgent_{fog_node_id}",
            agent_name="Clinical AI & Decision-Making Agent",
            fog_node_id=fog_node_id,
            bus=bus
        )
        self.classifier = classifier
        self.db = db
        self.clinical_alerts_count = 0

    def on_message(self, message: AgentMessage):
        if message.action == "CLINICAL_AI_EVALUATION":
            self.evaluate_patient_data(message.payload)

    def evaluate_patient_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        self.state = "PROCESSING"
        self.processed_count += 1

        payload = data.get("payload", {})
        patient_id = data.get("patient_id", "P-UNKNOWN")
        patient_name = payload.get("patient_name", f"Patient-{patient_id}")
        department = payload.get("department", "ICU")

        # Execute AI Vital Sign Evaluation
        result = self.classifier.evaluate_vitals(payload)
        triage_level = result["triage_level"]

        # Cache in local Fog SQLite Database
        self.db.log_vital(payload, triage_level.value, self.fog_node_id)

        # If Critical or Warning, trigger high-priority clinical alert
        if result["is_emergency"] or triage_level == VitalTriageLevel.WARNING:
            self.state = "ALERTING"
            self.clinical_alerts_count += 1
            
            alert = ClinicalAlert(
                alert_id=f"MED_{int(datetime.now().timestamp()*1000)}_{patient_id[-4:]}",
                patient_id=patient_id,
                patient_name=patient_name,
                triage_level=triage_level,
                abnormal_metrics=result["abnormal_metrics"],
                diagnosis_flag=result["diagnosis_flag"],
                confidence=result["confidence"],
                recommended_action=result["recommended_action"],
                fog_node_id=self.fog_node_id,
                timestamp=datetime.now().timestamp()
            )

            self.db.log_clinical_alert(alert.model_dump())

            # Notify Resource Agent and Cloud Management
            self.send_message(
                receiver=f"ResourceAgent_{self.fog_node_id}",
                action="CLINICAL_EMERGENCY_DETECTED",
                payload=alert.model_dump()
            )
            self.send_message(
                receiver="CloudCoordinatorAgent",
                action="EMERGENCY_TRIAGE_SYNC",
                payload=alert.model_dump()
            )

        self.state = "IDLE"
        return result
