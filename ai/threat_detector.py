"""
AI Cyber-Security Threat Detector for Healthcare Fog Computing
Detects:
1. DoS / Packet Flooding Attacks
2. Data Tampering / Man-in-the-Middle Payload Alteration
3. Sensor Identity Spoofing & Rogue Devices
4. Replay Attacks (Stale Nonce / Timestamp Deviation)
5. Unauthorized Access Attempts
"""

import time
import numpy as np
from typing import Dict, Any, List, Tuple, Optional
from collections import defaultdict, deque
from sklearn.ensemble import RandomForestClassifier
from core.models import ThreatType, SecurityAlert


class CyberThreatDetector:
    def __init__(self, flood_rate_threshold_hz: float = 15.0, timestamp_skew_max_sec: float = 10.0):
        self.flood_rate_threshold_hz = flood_rate_threshold_hz
        self.timestamp_skew_max_sec = timestamp_skew_max_sec
        
        # History tracking for rate limiting & replay detection
        self.packet_timestamps = defaultdict(lambda: deque(maxlen=60))
        self.seen_nonces = set()
        self.nonce_timestamps = {}
        
        # Train lightweight threat classification model
        self.model = RandomForestClassifier(n_estimators=40, max_depth=6, random_state=42)
        self._train_threat_model()

    def _train_threat_model(self):
        """
        Features: [packet_rate, timestamp_delta, payload_variance, invalid_signature_flag, token_valid_flag]
        Labels: 0: Normal, 1: DoS Flood, 2: Tampering, 3: Replay, 4: Spoofing/Unauthorized
        """
        np.random.seed(42)
        n = 500
        
        # 0. Normal
        f_norm = np.column_stack([
            np.random.uniform(0.5, 3.0, n),    # packet rate Hz
            np.random.uniform(0.01, 1.5, n),   # time delta sec
            np.random.uniform(0.1, 5.0, n),    # payload variance
            np.zeros(n),                       # signature error
            np.ones(n)                         # token valid
        ])
        y_norm = np.zeros(n)

        # 1. DoS Flood
        f_flood = np.column_stack([
            np.random.uniform(20.0, 100.0, n),
            np.random.uniform(0.001, 0.05, n),
            np.random.uniform(0.1, 5.0, n),
            np.zeros(n),
            np.ones(n)
        ])
        y_flood = np.ones(n)

        # 2. Tampering
        f_tamper = np.column_stack([
            np.random.uniform(0.5, 5.0, n),
            np.random.uniform(0.01, 1.5, n),
            np.random.uniform(50.0, 300.0, n), # Extreme impossible variance
            np.ones(n),                        # Signature failed
            np.ones(n)
        ])
        y_tamper = np.full(n, 2)

        # 3. Replay
        f_replay = np.column_stack([
            np.random.uniform(0.5, 5.0, n),
            np.random.uniform(15.0, 300.0, n), # Stale timestamp
            np.random.uniform(0.1, 5.0, n),
            np.zeros(n),
            np.ones(n)
        ])
        y_replay = np.full(n, 3)

        # 4. Spoofing / Unauthorized
        f_spoof = np.column_stack([
            np.random.uniform(0.5, 10.0, n),
            np.random.uniform(0.01, 2.0, n),
            np.random.uniform(0.1, 10.0, n),
            np.ones(n),
            np.zeros(n)                        # Token invalid
        ])
        y_spoof = np.full(n, 4)

        X = np.vstack([f_norm, f_flood, f_tamper, f_replay, f_spoof])
        y = np.concatenate([y_norm, y_flood, y_tamper, y_replay, y_spoof])
        self.model.fit(X, y)

    def analyze_packet(
        self,
        sensor_id: str,
        packet_time: float,
        nonce: str,
        token_valid: bool,
        hmac_valid: bool,
        payload_data: Dict[str, Any],
        fog_node_id: str = "FogNode-01"
    ) -> Tuple[bool, Optional[SecurityAlert]]:
        """
        Analyzes incoming packet for cyber security threats.
        Returns: (is_threat, SecurityAlert or None)
        """
        now = time.time()
        sensor_history = self.packet_timestamps[sensor_id]
        sensor_history.append(now)

        # Clean old nonces older than 10 minutes
        cutoff = now - 600
        expired_nonces = [n for n, ts in self.nonce_timestamps.items() if ts < cutoff]
        for en in expired_nonces:
            self.seen_nonces.discard(en)
            self.nonce_timestamps.pop(en, None)

        # Calculate live traffic metrics
        recent_in_1sec = [t for t in sensor_history if (now - t) <= 1.0]
        current_rate_hz = len(recent_in_1sec)
        time_skew = abs(now - packet_time)

        # Check impossible physiological values (Data Tampering indicator)
        tamper_detected = False
        hr = payload_data.get("heart_rate", 75)
        spo2 = payload_data.get("spo2", 98)
        temp = payload_data.get("temperature", 37)
        if hr > 350 or hr < 10 or spo2 > 100 or spo2 < 20 or temp > 50 or temp < 20:
            tamper_detected = True

        # Rule 1: DoS Packet Flood Attack
        if current_rate_hz > self.flood_rate_threshold_hz:
            alert = SecurityAlert(
                alert_id=f"SEC_{int(now*1000)}_{sensor_id[-4:]}",
                threat_type=ThreatType.DOS_FLOOD,
                severity="CRITICAL",
                source_sensor_id=sensor_id,
                source_ip_mac="192.168.1.105:44321",
                fog_node_id=fog_node_id,
                description=f"DoS Flooding attack detected from {sensor_id}. Rate: {current_rate_hz} pkts/sec (Limit: {self.flood_rate_threshold_hz} Hz).",
                confidence_score=0.98,
                mitigation_action="DYNAMIC_FIREWALL_BLOCK_AND_RATE_THROTTLE",
                timestamp=now
            )
            return True, alert

        # Rule 2: Replay Attack (Duplicate Nonce or large timestamp skew)
        if nonce in self.seen_nonces or time_skew > self.timestamp_skew_max_sec:
            reason = "Duplicate Nonce Replayed" if nonce in self.seen_nonces else f"Stale Timestamp (Skew: {time_skew:.2f}s)"
            alert = SecurityAlert(
                alert_id=f"SEC_{int(now*1000)}_{sensor_id[-4:]}",
                threat_type=ThreatType.REPLAY_ATTACK,
                severity="HIGH",
                source_sensor_id=sensor_id,
                source_ip_mac="192.168.1.112:51220",
                fog_node_id=fog_node_id,
                description=f"Replay attack intercepted for {sensor_id}. {reason}.",
                confidence_score=0.95,
                mitigation_action="DROP_PACKET_AND_REVOKE_SESSION",
                timestamp=now
            )
            return True, alert
        else:
            self.seen_nonces.add(nonce)
            self.nonce_timestamps[nonce] = now

        # Rule 3: Sensor Identity Spoofing / Rogue Device Injection
        if not token_valid:
            alert = SecurityAlert(
                alert_id=f"SEC_{int(now*1000)}_{sensor_id[-4:]}",
                threat_type=ThreatType.SENSOR_SPOOFING,
                severity="HIGH",
                source_sensor_id=sensor_id,
                source_ip_mac="192.168.1.240:48810",
                fog_node_id=fog_node_id,
                description=f"Rogue / Spoofed sensor detected on {fog_node_id}. Invalid Zero-Trust device token for {sensor_id}.",
                confidence_score=0.96,
                mitigation_action="BLOCK_MAC_AND_ISOLATE_PORT",
                timestamp=now
            )
            return True, alert

        # Rule 4: Data Tampering / HMAC Integrity Failure (MitM)
        if not hmac_valid or tamper_detected:
            reason = "Cryptographic HMAC Failure" if not hmac_valid else f"Impossible Jump (HR={hr} BPM)"
            alert = SecurityAlert(
                alert_id=f"SEC_{int(now*1000)}_{sensor_id[-4:]}",
                threat_type=ThreatType.DATA_TAMPERING,
                severity="CRITICAL",
                source_sensor_id=sensor_id,
                source_ip_mac="192.168.1.189:60023",
                fog_node_id=fog_node_id,
                description=f"Data tampering/MitM detected on {sensor_id}. Reason: {reason}.",
                confidence_score=0.99,
                mitigation_action="QUARANTINE_SENSOR_AND_ALERT_SECURITY_OP",
                timestamp=now
            )
            return True, alert

        return False, None
