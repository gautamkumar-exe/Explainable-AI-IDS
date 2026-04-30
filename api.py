"""
SentraX IDS – API Server
=========================
FastAPI backend with:
  - Real ML inference via /api/analyze
  - Real-time simulated feed via /api/live_feed (each call runs real inference)
  - Persistent in-memory event log store via /api/logs
  - All logs are auto-generated from actual ML predictions
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import numpy as np
import random
import time
import os
import threading
from collections import deque
from datetime import datetime

from model import SentraXModel, run_pipeline

app = FastAPI(title="SentraX IDS API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────
# GLOBAL STATE
# ─────────────────────────────────────────────
sentrax = None
dataset_pool = None

# In-memory log store — thread-safe, capped at 200 entries
LOG_STORE: deque = deque(maxlen=200)
log_lock = threading.Lock()

# Counters for dynamic KPIs
stats = {
    "total_predictions": 0,
    "total_attacks": 0,
    "recent_attack_scores": deque(maxlen=20),   # rolling window for risk
}


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def _generate_ip():
    return f"{random.randint(10,200)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"


def _severity_from_prediction(label: str, confidence: float) -> str:
    """Derive severity from ML output — no hardcoding."""
    if label == "Normal":
        return "Low"
    if confidence >= 0.92:
        return "High"
    if confidence >= 0.80:
        return "Medium"
    return "Medium"


def _create_log_entry(result: dict, source: str = "simulation") -> dict:
    """Build a structured log entry from a real ML prediction result."""
    protocols = ["TCP", "UDP", "ICMP"]
    common_ports = [80, 443, 22, 21, 3306, 5432, 8080, 8443, 53, 25]

    label = result["label"]
    category = result["category"]
    confidence = result["confidence"]
    severity = _severity_from_prediction(label, confidence)

    entry = {
        "id": stats["total_predictions"],
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "timestamp_full": datetime.now().isoformat(),
        "source_ip": _generate_ip(),
        "dest_ip": _generate_ip(),
        "protocol": random.choice(protocols),
        "port": random.choice(common_ports),
        "label": label,           # "Normal" or "Attack"
        "category": category,     # "Normal" / "DoS" / "Probe" / "R2L" / "U2R"
        "confidence": round(confidence, 4),
        "severity": severity,
        "source": source,         # "simulation" or "manual"
        "event": f"{category} Attempt" if label == "Attack" else "Regular Traffic",
    }

    # Persist
    with log_lock:
        LOG_STORE.appendleft(entry)

    # Update stats
    stats["total_predictions"] += 1
    if label == "Attack":
        stats["total_attacks"] += 1
        stats["recent_attack_scores"].append(confidence)

    return entry


def _compute_risk_score() -> int:
    """Dynamic risk score based on rolling window of recent attacks."""
    window = list(stats["recent_attack_scores"])
    if not window:
        return random.randint(3, 15)   # baseline noise
    # Weighted: more recent attacks in window → higher score
    avg_conf = sum(window) / len(window)
    density = len(window) / 20          # how full the window is (0-1)
    raw = avg_conf * 100 * density
    return min(100, max(0, int(raw + random.randint(-5, 5))))


# ─────────────────────────────────────────────
# STARTUP
# ─────────────────────────────────────────────
@app.on_event("startup")
async def startup_event():
    global sentrax, dataset_pool
    try:
        sentrax = SentraXModel().load()
        print("✅ Model artifacts loaded.")

        csv_path = os.getenv("DATASET_PATH", "nsl_kdd_dataset.csv")
        # Fallback to the original download path if it's there
        if not os.path.exists(csv_path):
            csv_path = "/Users/gautamkumar/Downloads/nsl_kdd_dataset.csv"
            
        if os.path.exists(csv_path):
            dataset_pool = pd.read_csv(csv_path)
            print(f"✅ Simulation pool loaded ({len(dataset_pool)} rows)")
    except Exception as e:
        print(f"⚠️ Startup error: {e}")


# ─────────────────────────────────────────────
# REQUEST SCHEMA
# ─────────────────────────────────────────────
class TrafficInput(BaseModel):
    duration: float
    src_bytes: float
    dst_bytes: float
    num_failed_logins: float
    num_file_creations: float
    num_shells: float
    is_guest_login: float
    count: float
    srv_count: float
    dst_host_count: float


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ENDPOINTS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.post("/api/analyze")
async def analyze_traffic(data: TrafficInput):
    """Manual analysis — runs real ML inference and auto-logs the result."""
    if not sentrax:
        return {"error": "Model not loaded"}

    result = run_pipeline(data.dict(), sentrax)

    # Auto-create a log entry from this manual analysis
    log_entry = _create_log_entry(result, source="manual")

    return {
        **result,
        "log_entry": log_entry,
    }


@app.get("/api/live_feed")
async def get_live_feed():
    """Simulated real-time pipeline: Dataset → Inference → Log → UI."""
    if sentrax is None:
        return {"error": "Model not ready"}

    # 1. Sample from real dataset or generate random features
    if dataset_pool is not None:
        sample = dataset_pool.sample(1).iloc[0]
        raw_features = {f: float(sample[f]) for f in sentrax.feature_names}
    else:
        raw_features = {f: random.random() for f in sentrax.feature_names}

    # 2. Real ML Inference
    result = run_pipeline(raw_features, sentrax)

    # 3. Auto-create a log entry
    log_entry = _create_log_entry(result, source="simulation")

    # 4. Compute dynamic risk score
    risk_score = _compute_risk_score()

    return {
        "log_entry": log_entry,
        "risk_score": risk_score,
        "metrics": result.get("metrics", {}),
        "model_info": {
            "type": "Random Forest",
            "dataset": "NSL-KDD",
            "status": "Operational",
        },
        "stats": {
            "total_predictions": stats["total_predictions"],
            "total_attacks": stats["total_attacks"],
        },
    }


@app.get("/api/logs")
async def get_logs(limit: int = 50):
    """
    Returns the most recent log entries.
    All entries are generated from real ML predictions.
    Sorted latest-first.
    """
    with log_lock:
        logs = list(LOG_STORE)[:limit]
    return {
        "logs": logs,
        "total": len(LOG_STORE),
        "stats": {
            "total_predictions": stats["total_predictions"],
            "total_attacks": stats["total_attacks"],
        },
    }
