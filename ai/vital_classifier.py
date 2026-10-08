"""
AI Vital Sign Clinical Classifier & Anomaly Detector
Machine Learning model for real-time patient triage at the Fog Layer.
Detects:
- Tachycardia, Bradycardia
- Hypoxemia / Respiratory Distress
- Hypertensive Crisis / Hypotension
- Hyperglycemia / Hypoglycemia
- Sepsis / High Fever
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple, List
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from core.models import VitalTriageLevel


class VitalSignAIClassifier:
    def __init__(self):
        self.classifier = RandomForestClassifier(n_estimators=60, max_depth=8, random_state=42)
        self.anomaly_detector = IsolationForest(contamination=0.08, random_state=42)
        self.feature_names = [
            "heart_rate", "spo2", "systolic_bp", "diastolic_bp",
            "temperature", "blood_glucose", "respiratory_rate"
        ]
        self._train_models()

    def _generate_synthetic_dataset(self, n_samples: int = 4000) -> Tuple[np.ndarray, np.ndarray]:
        """Generates realistic synthetic multi-parameter physiological dataset."""
        np.random.seed(42)
        half = n_samples // 2

        # 1. Normal physiological vitals (Class 0)
        norm_hr = np.random.normal(75, 8, half)
        norm_spo2 = np.random.normal(98, 1.2, half)
        norm_sbp = np.random.normal(120, 8, half)
        norm_dbp = np.random.normal(80, 6, half)
        norm_temp = np.random.normal(36.8, 0.4, half)
        norm_glucose = np.random.normal(100, 15, half)
        norm_rr = np.random.normal(16, 2, half)
        X_normal = np.column_stack([norm_hr, norm_spo2, norm_sbp, norm_dbp, norm_temp, norm_glucose, norm_rr])
        y_normal = np.zeros(half, dtype=int)

        # 2. Abnormal / Critical conditions (Classes 1: Warning, 2: Critical)
        sub = half // 5
        # 2a. Tachycardia / Arrhythmia
        abn1_hr = np.random.uniform(130, 180, sub)
        abn1_spo2 = np.random.uniform(92, 97, sub)
        abn1_sbp = np.random.uniform(120, 150, sub)
        abn1_dbp = np.random.uniform(80, 95, sub)
        abn1_temp = np.random.uniform(36.5, 37.8, sub)
        abn1_glucose = np.random.uniform(90, 140, sub)
        abn1_rr = np.random.uniform(20, 32, sub)
        X_abn1 = np.column_stack([abn1_hr, abn1_spo2, abn1_sbp, abn1_dbp, abn1_temp, abn1_glucose, abn1_rr])
        y_abn1 = np.full(sub, 2)  # Critical

        # 2b. Hypoxemia / Respiratory failure
        abn2_hr = np.random.uniform(100, 135, sub)
        abn2_spo2 = np.random.uniform(70, 88, sub)
        abn2_sbp = np.random.uniform(105, 140, sub)
        abn2_dbp = np.random.uniform(70, 90, sub)
        abn2_temp = np.random.uniform(36.5, 38.0, sub)
        abn2_glucose = np.random.uniform(90, 120, sub)
        abn2_rr = np.random.uniform(26, 40, sub)
        X_abn2 = np.column_stack([abn2_hr, abn2_spo2, abn2_sbp, abn2_dbp, abn2_temp, abn2_glucose, abn2_rr])
        y_abn2 = np.full(sub, 2)  # Critical

        # 2c. Hypertensive Crisis
        abn3_hr = np.random.uniform(90, 125, sub)
        abn3_spo2 = np.random.uniform(94, 99, sub)
        abn3_sbp = np.random.uniform(180, 230, sub)
        abn3_dbp = np.random.uniform(115, 140, sub)
        abn3_temp = np.random.uniform(36.5, 37.5, sub)
        abn3_glucose = np.random.uniform(100, 180, sub)
        abn3_rr = np.random.uniform(18, 26, sub)
        X_abn3 = np.column_stack([abn3_hr, abn3_spo2, abn3_sbp, abn3_dbp, abn3_temp, abn3_glucose, abn3_rr])
        y_abn3 = np.full(sub, 2)  # Critical

        # 2d. Septic Fever / Severe infection
        abn4_hr = np.random.uniform(110, 145, sub)
        abn4_spo2 = np.random.uniform(90, 95, sub)
        abn4_sbp = np.random.uniform(80, 100, sub)
        abn4_dbp = np.random.uniform(50, 65, sub)
        abn4_temp = np.random.uniform(39.2, 41.5, sub)
        abn4_glucose = np.random.uniform(140, 250, sub)
        abn4_rr = np.random.uniform(22, 35, sub)
        X_abn4 = np.column_stack([abn4_hr, abn4_spo2, abn4_sbp, abn4_dbp, abn4_temp, abn4_glucose, abn4_rr])
        y_abn4 = np.full(sub, 2)  # Critical

        # 2e. Mild Concern / Warning
        abn5_hr = np.random.uniform(95, 108, sub)
        abn5_spo2 = np.random.uniform(91, 94, sub)
        abn5_sbp = np.random.uniform(135, 150, sub)
        abn5_dbp = np.random.uniform(88, 96, sub)
        abn5_temp = np.random.uniform(37.6, 38.3, sub)
        abn5_glucose = np.random.uniform(130, 170, sub)
        abn5_rr = np.random.uniform(19, 23, sub)
        X_abn5 = np.column_stack([abn5_hr, abn5_spo2, abn5_sbp, abn5_dbp, abn5_temp, abn5_glucose, abn5_rr])
        y_abn5 = np.full(sub, 1)  # Warning

        X = np.vstack([X_normal, X_abn1, X_abn2, X_abn3, X_abn4, X_abn5])
        y = np.concatenate([y_normal, y_abn1, y_abn2, y_abn3, y_abn4, y_abn5])
        return X, y

    def _train_models(self):
        X, y = self._generate_synthetic_dataset(3000)
        self.classifier.fit(X, y)
        self.anomaly_detector.fit(X[y == 0])  # Fit on normal baseline

    def evaluate_vitals(self, vitals_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Infers triage level, detects abnormal parameters, and generates diagnosis & actions.
        """
        features = [
            float(vitals_dict.get("heart_rate", 75.0)),
            float(vitals_dict.get("spo2", 98.0)),
            float(vitals_dict.get("systolic_bp", 120.0)),
            float(vitals_dict.get("diastolic_bp", 80.0)),
            float(vitals_dict.get("temperature", 37.0)),
            float(vitals_dict.get("blood_glucose", 100.0)),
            float(vitals_dict.get("respiratory_rate", 16.0))
        ]

        X_input = np.array([features])
        pred_class = int(self.classifier.predict(X_input)[0])
        probabilities = self.classifier.predict_proba(X_input)[0]
        confidence = float(np.max(probabilities))
        anomaly_score = float(self.anomaly_detector.decision_function(X_input)[0])

        # Clinical rule check & abnormal metric extraction
        abnormal_metrics: List[str] = []
        diagnoses: List[str] = []

        hr, spo2, sbp, dbp, temp, bg, rr = features

        if hr > 115:
            abnormal_metrics.append(f"Tachycardia (HR={hr:.1f} bpm)")
            diagnoses.append("Arrhythmia / Extreme Tachycardia")
        elif hr < 50:
            abnormal_metrics.append(f"Bradycardia (HR={hr:.1f} bpm)")
            diagnoses.append("Severe Sinus Bradycardia")

        if spo2 < 90:
            abnormal_metrics.append(f"Severe Hypoxia (SpO2={spo2:.1f}%)")
            diagnoses.append("Acute Respiratory Distress")
        elif spo2 < 94:
            abnormal_metrics.append(f"Mild Hypoxia (SpO2={spo2:.1f}%)")

        if sbp >= 170 or dbp >= 110:
            abnormal_metrics.append(f"Hypertensive Crisis (BP={sbp:.0f}/{dbp:.0f} mmHg)")
            diagnoses.append("Hypertensive Emergency")
        elif sbp < 90 or dbp < 55:
            abnormal_metrics.append(f"Hypotension / Shock (BP={sbp:.0f}/{dbp:.0f} mmHg)")
            diagnoses.append("Hemodynamic Instability")

        if temp >= 39.0:
            abnormal_metrics.append(f"High Pyrexia/Fever (Temp={temp:.1f}°C)")
            diagnoses.append("Hyperthermia / Sepsis Risk")
        elif temp < 35.0:
            abnormal_metrics.append(f"Hypothermia (Temp={temp:.1f}°C)")

        if bg >= 220:
            abnormal_metrics.append(f"Hyperglycemia (Glucose={bg:.1f} mg/dL)")
            diagnoses.append("Diabetic Ketoacidosis Risk")
        elif bg < 65:
            abnormal_metrics.append(f"Hypoglycemia (Glucose={bg:.1f} mg/dL)")
            diagnoses.append("Acute Hypoglycemic Shock")

        # Map to enum
        if len(diagnoses) > 0 or pred_class == 2 or (anomaly_score < -0.2 and len(abnormal_metrics) > 0):
            triage_level = VitalTriageLevel.CRITICAL_EMERGENCY
            rec_action = "IMMEDIATE_ICU_NOTIFICATION_AND_OXYGEN_VASOPRESSOR_TRIAGE"
            diag_str = " | ".join(diagnoses) if diagnoses else "Multi-parameter Physiological Crisis"
        elif len(abnormal_metrics) > 0 or pred_class == 1:
            triage_level = VitalTriageLevel.WARNING
            rec_action = "CONTINUOUS_FOG_MONITORING_AND_NURSE_ALERT"
            diag_str = "Borderline Vitals Fluctuation"
        else:
            triage_level = VitalTriageLevel.NORMAL
            rec_action = "ROUTINE_MONITORING"
            diag_str = "Stable Physiological Condition"

        return {
            "triage_level": triage_level,
            "abnormal_metrics": abnormal_metrics,
            "diagnosis_flag": diag_str,
            "confidence": round(confidence, 4),
            "anomaly_score": round(anomaly_score, 4),
            "recommended_action": rec_action,
            "is_emergency": triage_level == VitalTriageLevel.CRITICAL_EMERGENCY
        }
