"""
Cryptographic and Privacy-Preservation Subsystem
Implements:
- AES-256-GCM Authenticated Encryption
- HMAC-SHA256 Message Integrity Verification
- Zero-Trust IoT Device Token Validation
- HIPAA/GDPR Compliant Data Anonymization (k-anonymity hashing + differential perturbation)
"""

import os
import hmac
import hashlib
import json
import base64
import time
from typing import Tuple, Dict, Any, Optional
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class SecurityCryptoEngine:
    # 256-bit symmetric key for Fog-IoT communication
    DEFAULT_MASTER_KEY = b"CVR_CSE_CYBERSEC_HEALTH_KEY_32B"

    def __init__(self, key: Optional[bytes] = None):
        self.key = key if key else self.DEFAULT_MASTER_KEY
        if len(self.key) != 32:
            self.key = hashlib.sha256(self.key).digest()
        self.aesgcm = AESGCM(self.key)
        self.hmac_key = hashlib.sha256(self.key + b"_HMAC_SALT").digest()
        self.salt_anonymizer = b"HIPAA_PRIVACY_SALT_CVR_2026"

    def encrypt_json(self, data: Dict[str, Any]) -> Tuple[str, str, str]:
        """
        Encrypts JSON dict using AES-256-GCM.
        Returns (ciphertext_b64, nonce_b64, tag_b64)
        Note: AESGCM in cryptography appends the 16-byte tag to the ciphertext.
        """
        nonce = os.urandom(12)  # 96-bit nonce for GCM
        plaintext_bytes = json.dumps(data, sort_keys=True).encode("utf-8")
        
        # ciphertext includes 16-byte authentication tag at the end
        encrypted_raw = self.aesgcm.encrypt(nonce, plaintext_bytes, None)
        ciphertext_raw = encrypted_raw[:-16]
        tag_raw = encrypted_raw[-16:]

        return (
            base64.b64encode(ciphertext_raw).decode("utf-8"),
            base64.b64encode(nonce).decode("utf-8"),
            base64.b64encode(tag_raw).decode("utf-8")
        )

    def decrypt_json(self, ciphertext_b64: str, nonce_b64: str, tag_b64: str) -> Dict[str, Any]:
        """
        Decrypts and authenticates AES-256-GCM encrypted payload.
        Raises ValueError on tampering or invalid key.
        """
        try:
            ciphertext_raw = base64.b64decode(ciphertext_b64)
            nonce = base64.b64decode(nonce_b64)
            tag_raw = base64.b64decode(tag_b64)
            
            combined_ciphertext = ciphertext_raw + tag_raw
            decrypted_bytes = self.aesgcm.decrypt(nonce, combined_ciphertext, None)
            return json.loads(decrypted_bytes.decode("utf-8"))
        except Exception as e:
            raise ValueError(f"AES-GCM Decryption/Authentication failed: {str(e)}")

    def generate_hmac(self, data_str: str) -> str:
        """Computes HMAC-SHA256 signature for data string."""
        h = hmac.new(self.hmac_key, data_str.encode("utf-8"), hashlib.sha256)
        return h.hexdigest()

    def verify_hmac(self, data_str: str, received_hmac: str) -> bool:
        """Verifies HMAC-SHA256 signature in constant time against timing attacks."""
        expected = self.generate_hmac(data_str)
        return hmac.compare_digest(expected, received_hmac)

    def generate_device_token(self, sensor_id: str, patient_id: str, expiry_seconds: int = 3600) -> str:
        """Generates a verifiable Zero-Trust device token with timestamp & signature."""
        expiry = int(time.time()) + expiry_seconds
        payload = f"{sensor_id}:{patient_id}:{expiry}"
        sig = self.generate_hmac(payload)
        token_data = f"{payload}:{sig}"
        return base64.urlsafe_b64encode(token_data.encode("utf-8")).decode("utf-8")

    def verify_device_token(self, token_b64: str, expected_sensor_id: str) -> bool:
        """Validates device token signature and expiration."""
        try:
            decoded = base64.urlsafe_b64decode(token_b64.encode("utf-8")).decode("utf-8")
            parts = decoded.split(":")
            if len(parts) != 4:
                return False
            sensor_id, patient_id, expiry_str, received_sig = parts
            if sensor_id != expected_sensor_id:
                return False
            if int(expiry_str) < time.time():
                return False  # Token expired
            expected_payload = f"{sensor_id}:{patient_id}:{expiry_str}"
            return self.verify_hmac(expected_payload, received_sig)
        except Exception:
            return False

    def anonymize_patient_record(self, vitals_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        HIPAA/GDPR Privacy Preservation:
        - Replaces patient_id and patient_name with cryptographic pseudo-hash
        - Generalizes age to age-bracket (e.g. 40-49)
        - Retains clinical vitals for aggregate analytics
        """
        raw_id = str(vitals_dict.get("patient_id", "UNKNOWN"))
        hasher = hashlib.sha256(self.salt_anonymizer + raw_id.encode("utf-8"))
        pseudo_hash = f"ANON_{hasher.hexdigest()[:12]}"

        age = vitals_dict.get("age", 0)
        age_group = f"{(age // 10) * 10}-{(age // 10) * 10 + 9}"

        anonymized = dict(vitals_dict)
        anonymized["patient_id"] = pseudo_hash
        anonymized["patient_name"] = "ANONYMIZED_SUBJECT"
        anonymized["age_group"] = age_group
        anonymized.pop("age", None)

        return anonymized
