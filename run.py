"""
One-Command Launcher for AI-Driven Multi-Agent Adaptive Fog Computing Framework
Secure Smart Healthcare Domain
CVR College of Engineering - CSE (Cyber Security)
"""

import os
import sys
import uvicorn
import webbrowser
import threading
import time

def open_browser():
    time.sleep(1.5)
    url = "http://127.0.0.1:8000"
    print(f"\n[+] Opening Smart Healthcare Dashboard: {url}\n")
    webbrowser.open(url)

if __name__ == "__main__":
    print("=" * 80)
    print("  AI-DRIVEN MULTI-AGENT ADAPTIVE FOG COMPUTING FRAMEWORK FOR SECURE HEALTHCARE")
    print("  Smart Healthcare IoMT System")
    print("=" * 80)
    print("[*] Initializing Multi-Agent Bus (Monitoring, Security, Decision, Resource)...")
    print("[*] Initializing AES-256-GCM Cryptographic Engine and Zero-Trust System...")
    print("[*] Training / Loading AI Vital Classifier and Cyber Threat Detectors...")
    print("[*] Starting Fog Computing Nodes (FogNode-01 ICU, FogNode-02 Cardio, FogNode-03 Outpatient)...")
    print("[*] Starting FastAPI Server on http://127.0.0.1:8000 ...")

    threading.Thread(target=open_browser, daemon=True).start()
    uvicorn.run("api.app:app", host="127.0.0.1", port=8000, reload=False)
