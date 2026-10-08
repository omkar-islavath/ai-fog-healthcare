"""
SQLite Database Engine for Local Fog Storage and Cloud Central Repository
"""

import sqlite3
import json
from typing import List, Dict, Any, Optional
from datetime import datetime


class HealthcareDatabase:
    def __init__(self, db_path: str = "fog_healthcare.db"):
        self.db_path = db_path
        self.init_schema()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_schema(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # 1. Local Vitals Caching Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS vitals_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id TEXT,
                patient_name TEXT,
                department TEXT,
                heart_rate REAL,
                spo2 REAL,
                systolic_bp REAL,
                diastolic_bp REAL,
                temperature REAL,
                blood_glucose REAL,
                respiratory_rate REAL,
                triage_level TEXT,
                fog_node_id TEXT,
                timestamp REAL
            )
            """)

            # 2. Security Alerts Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS security_alerts (
                alert_id TEXT PRIMARY KEY,
                threat_type TEXT,
                severity TEXT,
                source_sensor_id TEXT,
                source_ip_mac TEXT,
                fog_node_id TEXT,
                description TEXT,
                confidence_score REAL,
                mitigation_action TEXT,
                timestamp REAL
            )
            """)

            # 3. Clinical Alerts Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS clinical_alerts (
                alert_id TEXT PRIMARY KEY,
                patient_id TEXT,
                patient_name TEXT,
                triage_level TEXT,
                abnormal_metrics TEXT,
                diagnosis_flag TEXT,
                confidence REAL,
                recommended_action TEXT,
                fog_node_id TEXT,
                timestamp REAL
            )
            """)

            # 4. Fog Node Metrics Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS fog_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                node_id TEXT,
                cpu_utilization REAL,
                memory_utilization REAL,
                active_connections INTEGER,
                queue_latency_ms REAL,
                sampling_rate_hz REAL,
                offloaded_tasks INTEGER,
                threats_blocked INTEGER,
                timestamp REAL
            )
            """)

            # 5. Cloud Anonymized Repository Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS cloud_records (
                sync_id TEXT PRIMARY KEY,
                fog_node_id TEXT,
                anonymized_patient_hash TEXT,
                aggregated_vitals_json TEXT,
                triage_summary TEXT,
                security_event_count INTEGER,
                timestamp REAL
            )
            """)

            # 6. Dynamic Firewall / Quarantined Sensors
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS quarantined_devices (
                sensor_id TEXT PRIMARY KEY,
                reason TEXT,
                quarantined_at REAL,
                fog_node_id TEXT
            )
            """)

            conn.commit()

    def log_vital(self, data: Dict[str, Any], triage_level: str, fog_node_id: str):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO vitals_logs (
                patient_id, patient_name, department, heart_rate, spo2,
                systolic_bp, diastolic_bp, temperature, blood_glucose,
                respiratory_rate, triage_level, fog_node_id, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data.get("patient_id"),
                data.get("patient_name"),
                data.get("department", "ICU"),
                data.get("heart_rate"),
                data.get("spo2"),
                data.get("systolic_bp"),
                data.get("diastolic_bp"),
                data.get("temperature"),
                data.get("blood_glucose"),
                data.get("respiratory_rate", 16.0),
                triage_level,
                fog_node_id,
                data.get("timestamp", datetime.now().timestamp())
            ))
            conn.commit()

    def log_security_alert(self, alert: Dict[str, Any]):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT OR REPLACE INTO security_alerts (
                alert_id, threat_type, severity, source_sensor_id,
                source_ip_mac, fog_node_id, description, confidence_score,
                mitigation_action, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                alert["alert_id"],
                alert["threat_type"],
                alert["severity"],
                alert["source_sensor_id"],
                alert.get("source_ip_mac", "192.168.1.50"),
                alert["fog_node_id"],
                alert["description"],
                alert["confidence_score"],
                alert["mitigation_action"],
                alert.get("timestamp", datetime.now().timestamp())
            ))
            conn.commit()

    def log_clinical_alert(self, alert: Dict[str, Any]):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT OR REPLACE INTO clinical_alerts (
                alert_id, patient_id, patient_name, triage_level,
                abnormal_metrics, diagnosis_flag, confidence,
                recommended_action, fog_node_id, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                alert["alert_id"],
                alert["patient_id"],
                alert["patient_name"],
                alert["triage_level"],
                json.dumps(alert.get("abnormal_metrics", [])),
                alert["diagnosis_flag"],
                alert["confidence"],
                alert["recommended_action"],
                alert["fog_node_id"],
                alert.get("timestamp", datetime.now().timestamp())
            ))
            conn.commit()

    def quarantine_device(self, sensor_id: str, reason: str, fog_node_id: str):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT OR REPLACE INTO quarantined_devices (sensor_id, reason, quarantined_at, fog_node_id)
            VALUES (?, ?, ?, ?)
            """, (sensor_id, reason, datetime.now().timestamp(), fog_node_id))
            conn.commit()

    def is_quarantined(self, sensor_id: str) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM quarantined_devices WHERE sensor_id = ?", (sensor_id,))
            return cursor.fetchone() is not None

    def unquarantine_device(self, sensor_id: str):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM quarantined_devices WHERE sensor_id = ?", (sensor_id,))
            conn.commit()

    def get_recent_vitals(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM vitals_logs ORDER BY timestamp DESC LIMIT ?", (limit,))
            return [dict(row) for row in cursor.fetchall()]

    def get_recent_security_alerts(self, limit: int = 30) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM security_alerts ORDER BY timestamp DESC LIMIT ?", (limit,))
            return [dict(row) for row in cursor.fetchall()]

    def get_recent_clinical_alerts(self, limit: int = 30) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM clinical_alerts ORDER BY timestamp DESC LIMIT ?", (limit,))
            rows = []
            for r in cursor.fetchall():
                d = dict(r)
                if isinstance(d.get("abnormal_metrics"), str):
                    d["abnormal_metrics"] = json.loads(d["abnormal_metrics"])
                rows.append(d)
            return rows

    def get_quarantined_devices(self) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM quarantined_devices ORDER BY quarantined_at DESC")
            return [dict(row) for row in cursor.fetchall()]

    def log_cloud_sync(self, record: Dict[str, Any]):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT OR REPLACE INTO cloud_records (
                sync_id, fog_node_id, anonymized_patient_hash,
                aggregated_vitals_json, triage_summary, security_event_count, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                record["sync_id"],
                record["fog_node_id"],
                record["anonymized_patient_hash"],
                json.dumps(record.get("aggregated_vitals", {})),
                record["triage_summary"],
                record.get("security_event_count", 0),
                record.get("timestamp", datetime.now().timestamp())
            ))
            conn.commit()
